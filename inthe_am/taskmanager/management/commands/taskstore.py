from contextlib import contextmanager
import datetime
import json
import os
import traceback
import uuid
from typing import cast, Dict, Protocol
from inthe_am.taskmanager.models.usermetadata import UserMetadata

import progressbar

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.timezone import now

from inthe_am.taskmanager.models import TaskStore, TaskStoreStatistic
from inthe_am.taskmanager.lock import get_lock_redis


@contextmanager
def fast_git_checkpoint(
    store, message, function=None, args=None, kwargs=None, data=None
):
    checkpoint_id = uuid.uuid4()
    store.create_git_repository()

    try:
        store.create_git_checkpoint(
            message,
            function=function,
            args=args,
            kwargs=kwargs,
            pre_operation=True,
            checkpoint_id=checkpoint_id,
            data=data,
        )
        yield

        # We do not need to store undo.data since we're handling
        # history using a git repo and can revert using that.
        undo_path = os.path.join(store.local_path, "undo.data")
        if os.path.isfile(undo_path):
            os.unlink(undo_path)
        store.create_git_checkpoint(
            message,
            function=function,
            args=args,
            kwargs=kwargs,
            checkpoint_id=checkpoint_id,
            data=data,
        )
    except Exception:
        raise


class Subcommand(Protocol):
    def __call__(self, **options) -> None:
        ...


def handle_lock(**options):
    username = options["username"]
    minutes = options["minutes"]

    store = TaskStore.objects.get(user__username=username)
    store.set_lock_state(lock=True, seconds=minutes * 60)
    print(f"{store} locked")


def handle_unlock(**options):
    username = options["username"]

    store = TaskStore.objects.get(user__username=username)
    store.set_lock_state(lock=False)
    print(f"{store} unlocked")


def handle_search(**options):
    username = options["username"]

    users = User.objects.filter(
        Q(email__contains=username)
        | Q(username__contains=username)
        | Q(first_name__contains=username)
        | Q(last_name__contains=username)
    )
    for user in users:
        print(user.username)


def handle_list(**options):
    redis = get_lock_redis()
    for key in redis.keys("*.lock"):
        value = datetime.datetime.fromtimestamp(int(float(redis.get(key))))
        if value > datetime.datetime.utcnow():
            print(f"{key}: {value}")


def handle_update_statistics(**options):
    run_id = "update_statistics_{date}".format(
        date=datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    )
    print(f"Run ID: {run_id}")
    with progressbar.ProgressBar(
        max_value=TaskStore.objects.count(),
        widgets=[
            " [",
            progressbar.Timer(),
            "] ",
            progressbar.Bar(),
            " (",
            progressbar.ETA(),
            ") ",
        ],
    ) as bar:
        for idx, store in enumerate(TaskStore.objects.order_by("-last_synced")):
            TaskStoreStatistic.objects.create(
                store=store,
                measure=TaskStoreStatistic.MEASURE_SIZE,
                value=store.get_repository_size(),
                run_id=run_id,
            )
            bar.update(idx)


def handle_create_taskstore_accounts(**options):
    for store in TaskStore.objects.order_by("-last_synced"):
        store = cast(TaskStore, store)
        print(store)

        if not store.taskd_account.exists():
            try:
                user_key = store.taskrc["taskd.credentials"].split("/")[2]

                store.taskd_account.make_user_request(
                    "PUT",
                    data=json.dumps(
                        {
                            "user_key": user_key,
                        }
                    ),
                )
                print("> ACCOUNT CREATION OK")
            except Exception:
                print("> ACCOUNT CREATION FAILED")
                continue
        else:
            print("> ACCOUNT EXISTS")

        certs = store.taskd_account.make_user_request("GET", "certificates").json()
        if not certs:
            try:
                cert_fingerprint = store.taskrc.get_certificate_fingerprint()
                store.taskd_account.make_user_request(
                    "PUT",
                    data=json.dumps({}),
                    path=f"certificates/{cert_fingerprint}",
                )
                print("> CERT SET OK")
            except Exception:
                print("> CERT SET FAILED")
                continue
        else:
            print("> CERT ALREADY SET")


def handle_gc_large_repos(**options):
    squash_size = options["squash_size"]
    repack_size = options["repack_size"]

    for store in TaskStore.objects.order_by("-last_synced"):
        try:
            last_size_measurement = store.statistics.filter(
                measure=TaskStoreStatistic.MEASURE_SIZE
            ).latest("created")
        except TaskStoreStatistic.DoesNotExist:
            continue
        if last_size_measurement.value > squash_size:
            print(f"> Squashing {store}...")
            try:
                store.squash()
                store.gc()
                final_size = store.get_repository_size()
                print(
                    ">> {diff} MB recovered".format(
                        diff=int((last_size_measurement.value - final_size) / 1e6)
                    )
                )
            except Exception as e:
                print(f"> FAILED: {e}")
                traceback.print_exc()
        elif last_size_measurement.value > repack_size:
            print(f"> Repacking {store}...")
            try:
                store.gc()
                final_size = store.get_repository_size()
                print(
                    ">> {diff} MB recovered".format(
                        diff=int((last_size_measurement.value - final_size) / 1e6)
                    )
                )
            except Exception as e:
                print(f"> FAILED: {e}")
                traceback.print_exc()


def handle_squash(**options):
    username = options["username"]

    store = TaskStore.objects.get(user__username=username)

    starting_size = store.get_repository_size()

    store.squash(force=options["force"])
    store.gc()
    ending_size = store.get_repository_size()

    print(f">> {int((starting_size - ending_size) / 1000000.0)} MB recovered")


def handle_delete_old_accounts(**options):
    min_use_recency_days = options["min_use_recency_days"]

    min_action_recency = now() - datetime.timedelta(days=min_use_recency_days)
    for store in TaskStore.objects.filter(
        last_synced__lt=min_action_recency,
        user__last_login__lt=min_action_recency,
    ).order_by("-last_synced"):
        print(f"> Deleting {store.local_path}")
        store.delete()
        store.user.delete()


def handle_list_old_accounts(**options):
    min_use_recency_days = options["min_use_recency_days"]

    min_action_recency = now() - datetime.timedelta(days=min_use_recency_days)
    output_format = "{path}\t{last_synced}\t{last_login}"
    print(
        output_format.format(
            path="path",
            last_synced="last_synced",
            last_login="user__last_login",
        )
    )
    for store in TaskStore.objects.filter(
        last_synced__lt=min_action_recency,
        user__last_login__lt=min_action_recency,
    ).order_by("-last_synced"):
        print(
            output_format.format(
                path=store.local_path,
                last_synced=store.last_synced,
                last_login=store.user.last_login,
            )
        )


def handle_export(**options):
    username = options["username"] or ""

    for store in (
        TaskStore.objects.select_related("user")
        .filter(user__username__contains=username)
        .all()
    ):
        data = {
            "id": store.pk,
            "user": {"id": store.user.pk},
            "user__username": store.user.username,
            "configured": store.configured,
            "sync_enabled": store.sync_enabled,
            "sync_permitted": store.sync_permitted,
            "last_synced": (
                store.last_synced.isoformat() if store.last_synced else None
            ),
            "created": store.created.isoformat() if store.created else None,
            "updated": store.updated.isoformat() if store.updated else None,
            "errors": [],
        }

        try:
            valid = store.repository_is_valid()
            data["valid"] = valid
        except Exception as e:
            data["errors"].append(str(e))

        try:
            account_data = store.taskd_account.get()
            data.update(
                {
                    "account": {
                        "exists": store.taskd_account.exists(),
                        "created": account_data.get("created"),
                        "is_suspended": account_data.get("is_suspended"),
                    }
                }
            )
        except Exception as e:
            data["errors"].append(str(e))

        try:
            usermeta = UserMetadata.objects.get(user=store.user)
            data.update(
                {
                    "usermeta": {
                        "tos_version": usermeta.tos_version,
                        "tos_accepted": usermeta.tos_accepted.isoformat()
                        if usermeta.tos_accepted
                        else None,
                        "privacy_policy_version": usermeta.privacy_policy_version,
                        "privacy_policy_accepted": usermeta.privacy_policy_accepted.isoformat()
                        if usermeta.privacy_policy_accepted
                        else None,
                    }
                }
            )
        except UserMetadata.DoesNotExist as e:
            data["errors"].append(str(e))

        print(json.dumps(data))


class Command(BaseCommand):
    SUBCOMMANDS: Dict[str, Subcommand] = {
        "lock": handle_lock,
        "unlock": handle_unlock,
        "search": handle_search,
        "list": handle_list,
        "update_statistics": handle_update_statistics,
        "create_taskstore_accounts": handle_create_taskstore_accounts,
        "gc_large_repos": handle_gc_large_repos,
        "squash": handle_squash,
        "delete_old_accounts": handle_delete_old_accounts,
        "list_old_accounts": handle_list_old_accounts,
        "export": handle_export,
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "subcommand",
            nargs=1,
            choices=self.SUBCOMMANDS.keys(),
            type=str,
        )
        parser.add_argument("username", nargs="?", type=str)
        parser.add_argument(
            "--minutes",
            type=int,
            default=5,
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
        )
        parser.add_argument("--repack-size", type=int, default=int(1e7))
        parser.add_argument("--squash-size", type=int, default=int(5e7))
        parser.add_argument("--min-use-recency-days", type=int, default=370)

    def handle(self, *args, **options):
        return self.SUBCOMMANDS[options["subcommand"][0]](**options)
