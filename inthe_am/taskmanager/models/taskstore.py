import hashlib
import json
import logging
import os
import re
import subprocess
import tempfile
import time
import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.utils.timezone import now
from dulwich.client import NotGitRepository
from dulwich.repo import Repo
from rest_framework.authtoken.models import Token

from ..context_managers import git_checkpoint
from ..lock import (
    get_debounce_name_for_store,
    get_lock_name_for_store,
    get_lock_redis,
    redis_lock,
)
from ..tasks import deduplicate_tasks, sync_repository, sync_trello_tasks, update_trello
from ..taskstore_migrations import upgrade as upgrade_taskstore
from ..taskwarrior_client import TaskwarriorClient
from ..taskd import TaskdAccountManager
from ..utils import OneWaySafeJSONEncoder
from ..exceptions import InvalidTaskwarriorConfiguration
from .taskrc import TaskRc
from .metadata import Metadata
from .taskstoreactivitylog import TaskStoreActivityLog


logger = logging.getLogger(__name__)

HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


class TaskStore(models.Model):
    REPLY_ALL = 9
    REPLY_ERROR = 5
    REPLY_NEVER = 0
    REPLY_CHOICES = (
        (REPLY_ALL, "Reply to all messages",),
        (REPLY_ERROR, "Reply only to error messages",),
        (REPLY_NEVER, "Do not reply to any incoming text messages",),
    )

    DEFAULT_FILENAMES = {
        "key": "private.key.pem",
        "certificate": "private.certificate.pem",
        "ca_cert": "ca.certificate.pem",
    }

    user = models.ForeignKey(
        User,
        related_name="task_stores",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    local_path = models.CharField(max_length=255, blank=True,)

    configured = models.BooleanField(default=False)
    secret_id = models.CharField(blank=True, max_length=36)
    sync_enabled = models.BooleanField(default=True)
    sync_permitted = models.BooleanField(default=True)
    pebble_cards_enabled = models.BooleanField(default=False)
    feed_enabled = models.BooleanField(default=False)
    ical_enabled = models.BooleanField(default=False)

    taskrc_extras = models.TextField(blank=True)

    twilio_auth_token = models.CharField(max_length=32, blank=True)

    trello_auth_token = models.CharField(max_length=200, blank=True)
    trello_local_head = models.CharField(max_length=100, blank=True)

    sms_whitelist = models.TextField(blank=True)
    sms_arguments = models.TextField(blank=True)
    sms_replies = models.PositiveIntegerField(choices=REPLY_CHOICES, default=REPLY_ALL)

    auto_deduplicate = models.BooleanField(default=False)

    email_whitelist = models.TextField(blank=True)

    last_synced = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def username(self):
        try:
            return self.user.username
        except Exception:
            return "(None)"

    @property
    def version(self):
        return self.metadata.get("version", 0)

    @version.setter
    def version(self, value):
        self.metadata["version"] = value

    @property
    def metadata_registry(self):
        return os.path.join(self.local_path, ".meta")

    @property
    def metadata(self) -> Metadata:
        if not getattr(self, "_metadata", None):
            self._metadata = Metadata(self, self.metadata_registry)
        return self._metadata

    @property
    def taskrc(self) -> TaskRc:
        if not getattr(self, "_taskrc", None):
            self._taskrc = TaskRc(self.metadata["taskrc"])
        return self._taskrc

    @property
    def taskd_account(self) -> TaskdAccountManager:
        if not getattr(self, "_taskd_account", None):
            self._taskd_account = TaskdAccountManager(
                settings.TASKD_ORG, self.username,
            )

        return self._taskd_account

    @property
    def taskd_certificate_status(self):
        results = {}
        certificate_settings = (
            "taskd.certificate",
            "taskd.key",
            "taskd.ca",
        )
        for setting in certificate_settings:
            setting_value = setting.replace(".", "_")
            value = self.taskrc.get(setting, "")
            if not value:
                results[setting_value] = "No file available"
            elif "custom" in value:
                results[setting_value] = "Custom certificate in use"
            else:
                results[setting_value] = "Standard certificate in use"
        results["taskd_trust"] = self.taskrc.get("taskd.trust", "ignore hostname")
        return results

    @property
    def repository(self):
        return Repo(self.local_path)

    @classmethod
    def get_for_user(cls, user):
        store, created = TaskStore.objects.get_or_create(user=user,)
        if created:
            logger.info(f"Created new taskstore for {user}")
        upgrade_taskstore(store)
        return store

    @property
    def client(self):
        if not self.taskrc.get("data.location"):
            raise InvalidTaskwarriorConfiguration("No data.location specified!")

        if not getattr(self, "_client", None):
            self._client = TaskwarriorClient(
                self.taskrc.path,
                config_overrides=settings.TASKWARRIOR_CONFIG_OVERRIDES,
                store=self,  # Note that this will be a weak reference
            )
        return self._client

    def get_blocks_for_task(self, task):
        if not hasattr(self, "_blocks"):
            self._blocks = self.client.filter_tasks(
                {
                    "depends.not": "",
                    "or": [("status", "pending"), ("status", "waiting"),],
                }
            )

        blocks = []
        for other in self._blocks:
            if task["uuid"] in other.get("depends", ""):
                blocks.append(other["uuid"])

        return blocks

    def receive_client_message(self, name, *args, **kwargs):
        if name == "log":
            self._log_entry(*args, **kwargs)
        elif name == "metadata":
            if not hasattr(self, "_metadata_callbacks"):
                return

            for callback in self._metadata_callbacks.values():
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.exception(
                        "Error encountered while processing metadata " "callback: %s", e
                    )
        else:
            logger.error(
                "Unknown client message type %s", name,
            )

    @property
    def api_key(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        return token

    @property
    def trello_board(self):
        from .trelloobject import TrelloObject

        try:
            return TrelloObject.objects.get(
                store=self, type=TrelloObject.BOARD, deleted=False,
            )
        except TrelloObject.DoesNotExist:
            return None

    def _is_numeric(self, val):
        try:
            float(val)
            return True
        except (ValueError, TypeError):
            return False

    def _is_valid_type(self, val):
        if val in ("string", "numeric", "date", "duration"):
            return True
        return False

    def _is_valid_priority(self, val):
        if val in ("H", "M", "L"):
            return True
        return False

    def _get_extra_safely(self, key, val):
        valid_patterns = [
            (re.compile(r"^urgency\..*\.coefficient$"), self._is_numeric),
            (re.compile(r"^urgency\..*\.max$"), self._is_numeric),
            (re.compile(r"^uda\.priority\.default$"), self._is_valid_priority),
            (re.compile(r"^priority\.default$"), self._is_valid_priority),
            (re.compile(r"^uda\.[^.]+\.type$"), self._is_valid_type),
            (re.compile(r"^uda\.[^.]+\.label$"), lambda x: True),  # Accept all strings
        ]
        for pattern, verifier in valid_patterns:
            if pattern.match(key) and verifier(val):
                return True, None
            elif pattern.match(key):
                return False, f"Setting '{key}' has an invalid value."
        return False, f"Setting '{key}' could not be applied."

    def apply_extras(self):
        default_extras_path = os.path.join(self.local_path, ".taskrc_extras",)
        extras_path = self.metadata.get("taskrc_extras", default_extras_path)
        self.metadata["taskrc_extras"] = default_extras_path

        applied = {}
        errored = {}
        self.taskrc.add_include(extras_path)
        with tempfile.NamedTemporaryFile() as temp_extras:
            temp_extras.write(self.taskrc_extras.encode("utf-8"))
            temp_extras.flush()
            extras = TaskRc(temp_extras.name, read_only=True)

            with open(extras_path, "w") as applied_extras:
                for key, value in extras.items():
                    safe, message = self._get_extra_safely(key, value)
                    if safe:
                        applied[key] = value
                        applied_extras.write(f"{key}={value}\n")
                    else:
                        errored[key] = (value, message)
        return applied, errored

    def repository_is_valid(self):
        if not self.local_path:
            return False
        if not os.path.isdir(self.local_path):
            return False
        if not self.local_path.startswith(settings.TASK_STORAGE_PATH):
            return False
        try:
            self.repository.head().decode("utf-8")
        except KeyError:
            return False

        return True

    def save(self, *args, **kwargs):
        # Create the user directory
        if not self.repository_is_valid():
            user_tasks = os.path.join(settings.TASK_STORAGE_PATH, self.username,)
            if not os.path.isdir(user_tasks):
                os.mkdir(user_tasks)
            self.local_path = os.path.join(user_tasks, str(uuid.uuid4()))
            if not os.path.isdir(self.local_path):
                os.mkdir(self.local_path)
            with open(os.path.join(self.local_path, ".gitignore"), "w") as out:
                out.write(".lock\n")
            try:
                self.repository.head().decode("utf-8")
            except (KeyError, NotGitRepository):
                self.create_git_repository()

        if not self.secret_id:
            self.secret_id = str(uuid.uuid4())

        self.apply_extras()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            self.clear_local_task_list()
        except Exception as e:
            logger.exception(
                "Error encountered while deleting local task list: %s", e,
            )
        try:
            self.clear_taskserver_data()
        except Exception as e:
            logger.exception(
                "Error encountered while deleting taskserver task list: %s", e,
            )

        try:
            self.taskd_account.delete()
        except Exception as e:
            logger.exception(
                "Error encountered while deleting taskserver account: %s", e,
            )

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Tasks for {self.username}"

    #  Git-related methods

    def get_changed_task_ids(self, head, start=None):
        uuid_matcher = re.compile(r'uuid:"([0-9a-zA-Z-]+)"')
        if not start:
            start = self.repository.head().decode("utf-8")
        proc = self._git_command("diff", head, start)
        stdout, stderr = proc.communicate()
        changed_tickets = set()
        for raw_line in stdout.decode("utf-8", "ignore").split("\n"):
            line = raw_line.strip()
            if not line or line[0] not in ("+", "-"):
                continue
            matched = uuid_matcher.search(line)
            if matched:
                changed_tickets.add(matched.group(1))

        return changed_tickets

    def create_git_repository(self):
        self._simple_git_command("init")
        self.create_git_checkpoint("Initial Commit")
        return True

    def _git_command(self, *args):
        command = [
            "git",
            f"--work-tree={self.local_path}",
            f"--git-dir={os.path.join(self.local_path, '.git')}",
        ] + list(args)
        return subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

    def _simple_git_command(self, *args):
        proc = self._git_command(*args)
        stdout, stderr = proc.communicate()
        return proc.returncode

    def git_reset(self, to_sha):
        if to_sha is not None:
            self._simple_git_command("reset", "--hard", to_sha)
        else:
            self._simple_git_command("update-ref", "-d", "HEAD")

    def create_git_checkpoint(
        self,
        message,
        function=None,
        args=None,
        kwargs=None,
        pre_operation=False,
        rollback=False,
        checkpoint_id=None,
        force_commit=False,
        data=None,
    ):
        self._simple_git_command("add", "-A")
        commit_message = render_to_string(
            "git_checkpoint.txt",
            {
                "message": message,
                "function": function,
                "args": args,
                "kwargs": kwargs,
                "preop": pre_operation,
                "rollback": rollback,
                "checkpoint_id": checkpoint_id,
                "data": json.dumps(
                    data, indent=4, sort_keys=True, cls=OneWaySafeJSONEncoder,
                ),
            },
        )

        commit_args = [
            "commit",
            "--author",
            "Inthe.AM Git Bot <gitbot@inthe.am>",
            "-F",
            "-",
        ]

        if force_commit:
            commit_args.append("--allow-empty")

        proc = self._git_command(*commit_args)
        proc.stdin.write(commit_message.encode("utf-8", "replace"))
        proc.communicate()

    #  Taskd-related methods

    def has_active_checkpoint(self):
        client = get_lock_redis()
        lock_name = get_lock_name_for_store(self)

        result = client.get(lock_name)
        if result:
            return True
        return False

    @property
    def using_local_taskd(self):
        if not hasattr(self, "_local_taskd"):
            if self.taskrc["taskd.server"] == settings.TASKD_SERVER:
                self._local_taskd = True
            else:
                self._local_taskd = False
        return self._local_taskd

    @property
    def sync_uses_default_server(self):
        return self.taskrc.get("taskd.server") == settings.TASKD_SERVER

    def _get_queue_name(self, prefix="local_sync", suffix=None):
        base = f"{prefix}.{self.user.username}"
        if suffix is not None:
            return base + "." + suffix
        return base

    def _get_announcement_connection(self):
        if not hasattr(self, "_redis"):
            self._redis = get_lock_redis()

        return self._redis

    def publish_personal_announcement(self, message):
        self.publish_announcement("personal", message)

    def publish_announcement(self, prefix, message):
        connection = self._get_announcement_connection()
        connection.publish(
            self._get_queue_name(prefix=prefix),
            json.dumps(message, cls=DjangoJSONEncoder),
        )

    def deduplicate_tasks(self):
        debounce_key = get_debounce_name_for_store(self, "deduplication")
        defined_debounce_id = str(time.time())

        client = get_lock_redis()
        client.set(debounce_key, defined_debounce_id)

        deduplicate_tasks.apply_async(
            args=(self.pk,),
            kwargs={"debounce_id": defined_debounce_id,},
            countdown=10,  # To group multiple events together
        )

    def sync_trello(self, two_way=False):
        trello_sync_task = update_trello
        debounce_key = "trello_outgoing"

        if two_way:
            trello_sync_task = sync_trello_tasks
            debounce_key = "trello"

        debounce_key = get_debounce_name_for_store(self, debounce_key)
        defined_debounce_id = str(time.time())

        client = get_lock_redis()
        client.set(debounce_key, defined_debounce_id)
        trello_sync_task.apply_async(
            expires=3600,
            args=(self.pk,),
            kwargs={
                "debounce_id": defined_debounce_id,
                "current_head": self.repository.head().decode("utf-8"),
            },
        )

    def set_lock_state(self, lock=None, seconds=3600):
        lock_name = get_lock_name_for_store(self)
        client = get_lock_redis()

        if lock is True:
            return client.set(lock_name, str(time.time() + seconds))
        elif lock is False:
            return client.delete(lock_name)
        else:
            return client.get(lock_name)

    def get_repository_size(self):
        total_size = 0
        for dirpath, _, filenames in os.walk(self.local_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)

        return total_size

    def gc(self):
        with git_checkpoint(
            self,
            "Garbage Collection",
            notify_rollback=False,
            lock_timeout=60 * 120,  # 2h of lock timeout; just in case!
        ):
            reflog = self._git_command("reflog", "expire", "--expire=now", "--all")
            reflog_result = reflog.communicate()
            repack = self._git_command(
                "-c",
                "pack.windowMemory=30m",
                "-c",
                "pack.packSizeLimit=50m",
                "-c",
                "pack.threads=2",
                "gc",
                "--aggressive",
                "--prune=now",
            )
            repack_result = repack.communicate()

            results = {
                "reflog": {
                    "returncode": reflog.returncode,
                    "stdout": reflog_result[0].decode("utf-8"),
                    "stderr": reflog_result[1].decode("utf-8"),
                },
                "repack": {
                    "returncode": repack.returncode,
                    "stdout": repack_result[0].decode("utf-8"),
                    "stderr": repack_result[1].decode("utf-8"),
                },
            }
            return results

    def squash(self, force=False):
        lock_name = get_lock_name_for_store(self)

        with redis_lock(
            lock_name, message="Squash", lock_timeout=60 * 60, wait_timeout=60,
        ):
            if (
                self.trello_local_head
                and self.trello_local_head != self.repository.head().decode("utf-8")
                and not force
            ):
                raise ValueError("Trello head out-of-date; aborting!")

            head_commit, _ = self._git_command(
                "rev-list", "--max-parents=0", "HEAD",
            ).communicate()
            head_commit = head_commit.decode("utf-8").strip()

            self._git_command("reset", "--soft", head_commit,).communicate()

            self.create_git_checkpoint("Repository squashed.")

            if self.trello_local_head:
                self.trello_local_head = self.repository.head().decode("utf-8")
                self.save()

    def sync(self, function=None, args=None, kwargs=None, asynchronous=True, msg=None):
        if not self.sync_enabled or not self.sync_permitted:
            return False
        if not self.sync_uses_default_server:
            self.log_message(
                "Synchronization with other taskd servers is no longer "
                "supported.  Your account has been automatically reconfigured "
                "to synchronize with Inthe.AM's built-in task server."
                "You may need to re-configure your local taskwarrior "
                "instances."
            )
            self.reset_taskd_configuration()
            return True

        client = get_lock_redis()
        debounce_id = kwargs.get("debounce_id") if kwargs else None
        debounce_key = get_debounce_name_for_store(self)

        if asynchronous:
            defined_debounce_id = str(time.time())
            client.set(debounce_key, defined_debounce_id)
            sync_repository.apply_async(
                countdown=5,
                expires=3600,
                args=(self.pk,),
                kwargs={
                    "debounce_id": defined_debounce_id,
                    "current_head": self.repository.head().decode("utf-8"),
                },
            )
        else:
            try:
                expected_debounce_id = client.get(debounce_key)
            except (ValueError, TypeError):
                expected_debounce_id = None
            if (
                expected_debounce_id
                and debounce_id
                and (float(debounce_id) < float(expected_debounce_id))
            ):
                logger.warning(
                    "Debounce Failed: %s<%s; " "skipping synchronization for %s.",
                    debounce_id,
                    expected_debounce_id,
                    self.pk,
                )
                return
            elif expected_debounce_id and debounce_id:
                client.delete(debounce_key)
                logger.debug(
                    "Debounce Succeeded: %s>=%s for %s.",
                    debounce_id,
                    expected_debounce_id,
                    self.pk,
                )

            checkpoint_msg = "Synchronization"
            if msg:
                checkpoint_msg = f"{checkpoint_msg}: {msg}"

            start = self.repository.head().decode("utf-8")
            with git_checkpoint(
                self,
                checkpoint_msg,
                function=function,
                args=args,
                kwargs=kwargs,
                notify_rollback=False,
            ):
                self.client.sync()
                self.last_synced = now()
                self.save()

            head = self.repository.head().decode("utf-8")
            logger.info(
                "Emitting local_sync pubsub event for %s's " "task store at %s",
                self.username,
                self.local_path,
            )
            self.publish_announcement(
                "local_sync",
                {
                    "username": self.username,
                    "debounce_id": debounce_id,
                    "start": start,
                    "head": head,
                },
            )

            if (
                self.trello_auth_token
                and self.trello_board
                and (
                    not self.trello_local_head
                    or self.get_changed_task_ids(
                        self.repository.head().decode("utf-8"),
                        start=self.trello_local_head,
                    )
                )
            ):
                self.sync_trello()

        return True

    def reset_taskd_configuration(self):
        self.sync_permitted = False
        self.save()  # Just to make sure we don't sync while this is going on

        self.taskrc.update(
            {
                "taskd.certificate": os.path.join(
                    self.local_path, self.DEFAULT_FILENAMES["certificate"]
                ),
                "taskd.key": os.path.join(
                    self.local_path, self.DEFAULT_FILENAMES["key"]
                ),
                "taskd.ca": os.path.join(
                    self.local_path, self.DEFAULT_FILENAMES["ca_cert"]
                ),
                "taskd.trust": "ignore hostname",
                "taskd.server": settings.TASKD_SERVER,
                "taskd.credentials": self.metadata["generated_taskd_credentials"],
            }
        )
        self.generate_new_certificate()
        self.clear_taskserver_data()
        try:
            os.unlink(os.path.join(self.local_path, "backlog.data",))
        except OSError:
            pass
        self.sync_permitted = True
        self.save()
        self.client.sync(init=True)
        self.log_message("Taskd settings reset to default.")

    def clear_taskserver_data(self):
        self.taskd_account.delete_data()

    def clear_local_task_list(self):
        for path in os.listdir(self.local_path):
            if os.path.splitext(path)[1] == ".data":
                os.unlink(os.path.join(self.local_path, path))

    def autoconfigure_taskd(self):
        with git_checkpoint(self, "Autoconfiguration"):
            self.configured = True

            logger.warning(
                "%s just autoconfigured an account!", self.username,
            )

            # Remove any cached taskrc/taskw clients
            for attr in (
                "_taskrc",
                "_client",
            ):
                try:
                    delattr(self, attr)
                except AttributeError:
                    pass

            # Create and write a new private key
            private_key_proc = subprocess.Popen(
                ["certtool", "--generate-privkey",],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            private_key = private_key_proc.communicate()[0].decode("utf-8")
            private_key_filename = os.path.join(
                self.local_path, self.DEFAULT_FILENAMES["key"],
            )
            with open(private_key_filename, "w") as out:
                out.write(private_key)

        ca_cert_filename = os.path.join(
            self.local_path, self.DEFAULT_FILENAMES["ca_cert"],
        )
        with open(ca_cert_filename, "w") as out:
            out.write(self.taskd_account.get_ca_cert())

        self.taskd_account.create()
        credentials = self.taskd_account.get_credentials()
        with git_checkpoint(self, "Save initial taskrc credentials"):
            cert_data = self.generate_new_certificate()
            cert_filename = self.taskrc.get(
                "taskd.certificate",
                os.path.join(self.local_path, self.DEFAULT_FILENAMES["certificate"],),
            )

            with open(cert_filename, "w") as out:
                out.write(cert_data)

            self.taskrc.update(
                {
                    "data.location": self.local_path,
                    "taskd.certificate": cert_filename,
                    "taskd.key": private_key_filename,
                    "taskd.ca": ca_cert_filename,
                    "taskd.server": settings.TASKD_SERVER,
                    "taskd.credentials": credentials,
                    "taskd.trust": "ignore hostname",
                }
            )
            self.metadata["generated_taskd_credentials"] = credentials

        with git_checkpoint(self, "Initial Synchronization"):
            self.save()
            self.client.sync(init=True)

    def generate_new_certificate(self) -> str:
        private_key_filename = os.path.join(
            self.local_path, self.DEFAULT_FILENAMES["key"],
        )
        with tempfile.NamedTemporaryFile("w+") as signing_template:
            signing_template.write(self.taskd_account.get_signing_template())
            signing_template.flush()

            # Create and write a new certificate
            csr_proc = subprocess.Popen(
                [
                    "certtool",
                    "--generate-request",
                    "--load-privkey",
                    private_key_filename,
                    "--template",
                    signing_template.name,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            csr = csr_proc.communicate()[0].decode("utf-8")

        return self.taskd_account.get_new_certificate(csr)

    def register_metadata_callback(self, callback):
        if not hasattr(self, "_metadata_callbacks"):
            self._metadata_callbacks = {}

        random_uuid = str(uuid.uuid4())
        self._metadata_callbacks[random_uuid] = callback

        return random_uuid

    def unregister_metadata_callback(self, uid):
        del self._metadata_callbacks[uid]

    def register_logging_callback(self, callback):
        if not hasattr(self, "_logging_callbacks"):
            self._logging_callbacks = {}

        random_uuid = str(uuid.uuid4())
        self._logging_callbacks[random_uuid] = callback

        return random_uuid

    def unregister_logging_callback(self, uid):
        del self._logging_callbacks[uid]

    def _log_entry(self, message, error=False, params=None, silent=False):
        if params is None:
            params = []

        if hasattr(self, "_logging_callbacks"):
            for callback in self._logging_callbacks.values():
                try:
                    callback(message, *params)
                except Exception as e:
                    logger.exception("Error invoking logging callback: %s", e)

        message_hash = hashlib.md5(
            (self.local_path + message % params).encode("utf-8")
        ).hexdigest()
        instance, created = TaskStoreActivityLog.objects.get_or_create(
            store=self,
            md5hash=message_hash,
            defaults={
                "error": error,
                "silent": silent,
                "message": message % params,
                "count": 0,
            },
        )
        instance.count = instance.count + 1
        instance.last_seen = now()
        instance.save()
        return instance

    def log_message(self, message, *parameters):
        self._log_entry(message, error=False, params=parameters)

    def log_error(self, message, *parameters):
        self._log_entry(message, error=True, params=parameters)

    def log_silent_error(self, message, *parameters):
        self._log_entry(message, error=True, silent=True, params=parameters)

    def send_rest_hook_messages(self, task_id):
        for hook in self.rest_hooks.all():
            hook.send_message(task_id)

    class Meta:
        app_label = "taskmanager"
