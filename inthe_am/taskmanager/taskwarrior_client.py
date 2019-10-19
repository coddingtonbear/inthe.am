import curses.ascii
import datetime
import json
import logging
import pipes
import subprocess
import tempfile
import uuid
import weakref

import six
import taskw.utils
from taskw import TaskWarriorShellout, utils
from taskw.task import Task as TaskwTask

from inthe_am.taskmanager.utils import OneWaySafeJSONEncoder


logger = logging.getLogger(__name__)


class TaskwarriorError(Exception):
    def __init__(self, stderr, stdout, code):
        self.stderr = stderr.strip()
        self.stdout = stdout.strip()
        self.code = code
        message = "%s: %s :: %s" % (
            self.code,
            self.stdout,
            self.stderr
        )
        super(TaskwarriorError, self).__init__(message)


class TaskwarriorClient(TaskWarriorShellout):
    NONZERO_ALERT_EXEMPT = [
        'list',
    ]

    def __init__(self, *args, **kwargs):
        self.store = None
        if 'store' in kwargs:
            self.store = weakref.proxy(kwargs.pop('store'))
        super(TaskwarriorClient, self).__init__(*args, marshal=True, **kwargs)

    def send_client_message(self, name, *args, **kwargs):
        if not self.store:
            return

        try:
            self.store.receive_client_message(name, *args, **kwargs)
        except weakref.ReferenceError:
            pass

    def _get_acceptable_properties(self):
        return TaskwTask.FIELDS.keys() + self.config.get_udas().keys()

    def _get_acceptable_prefix(self, command):
        if ' ' in command:
            return command
        if command.lower() in self._get_acceptable_properties():
            return command.lower()
        return False

    def _get_json(self, *args):
        return json.loads(self._execute(*args)[0])

    def _strip_unsafe_args(self, *args):
        if not args:
            return args
        final_args = [args[0]]
        description_args = []
        for raw_arg in args[1:]:
            arg = self._strip_unsafe_chars(raw_arg)
            if ':' in arg:
                cmd, value = arg.split(':', 1)
                acceptable_cmd = self._get_acceptable_prefix(cmd)
                if acceptable_cmd:
                    final_args.append(
                        ':'.join(
                            [acceptable_cmd, value]
                        )
                    )
                else:
                    description_args.append(arg)
            elif arg.startswith('+') or arg.startswith('-'):
                final_args.append(arg)
            else:
                description_args.append(arg)

        return final_args + ['--'] + description_args

    def _strip_unsafe_chars(self, incoming):
        if isinstance(incoming, str):
            incoming = incoming.encode('utf8')
        return ''.join(
            char for char in incoming if curses.ascii.isprint(char)
        )

    def _execute_safe(self, *args):
        return self._execute(
            *self._strip_unsafe_args(*args)
        )

    def _get_logger(self, cmd):
        try:
            uuid.UUID(str(cmd[0]))
            command = str(cmd[1])
        except (ValueError, IndexError):
            command = str(cmd[0])
        return logging.getLogger('%s.%s' % (__name__, command))

    def gc(self):
        overrides = self.DEFAULT_CONFIG_OVERRIDES.copy()
        overrides.update(self.config_overrides)
        overrides['gc'] = 'on'

        try:
            self._execute(
                'list',
                config_overrides=overrides
            )
        except TaskwarriorError:
            # This is fine -- this will happen if there aren't any
            # entries in their task list.
            pass

    def _execute(self, *args, **kwargs):
        """ Execute a given taskwarrior command with arguments

        Returns a 2-tuple of stdout and stderr (respectively).

        """
        if 'config_overrides' in kwargs:
            config_overrides = utils.convert_dict_to_override_args(
                kwargs.pop('config_overrides')
            )
        else:
            config_overrides = self.get_configuration_override_args()

        logger = self._get_logger(args)

        command = (
            [
                'task',
                'rc:%s' % self.config_filename,
            ] +
            config_overrides +
            [six.text_type(arg) for arg in args]
        )

        # subprocess is expecting bytestrings only, so nuke unicode if present
        for i in range(len(command)):
            if isinstance(command[i], six.text_type):
                command[i] = (
                    taskw.utils.clean_ctrl_chars(command[i].encode('utf-8'))
                )

        started = datetime.datetime.now()

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        _stdout, _stderr = proc.communicate()
        stdout = _stdout.decode('utf-8')
        stderr = _stderr.decode('utf-8')

        total_seconds = (datetime.datetime.now() - started).total_seconds()

        self.send_client_message(
            'metadata',
            'taskwarrior.execute',
            {
                'command': ' '.join(
                    pipes.quote(c.decode('utf-8')) for c in command
                ),
                'arguments': ' '.join(
                    pipes.quote(six.text_type(arg)) for arg in args
                ),
                'stderr': stderr,
                'stdout': stdout,
                'returncode': proc.returncode,
                'duration': total_seconds,
            }
        )

        base_command = args[0]
        if (
            proc.returncode != 0 and
            base_command not in self.NONZERO_ALERT_EXEMPT
        ):
            logger.warning(
                'Non-zero return code returned from taskwarrior: %s; %s' % (
                    proc.returncode,
                    stderr,
                ),
                extra={
                    'stack': True,
                    'data': {
                        'code': proc.returncode,
                        'command': command,
                        'stdout': stdout,
                        'stderr': stderr,
                    }
                }
            )
            raise TaskwarriorError(stderr, stdout, proc.returncode)

        logger.debug("%s: %s", command, stdout)
        return stdout, stderr

    def import_task(self, value):
        with tempfile.NamedTemporaryFile() as jsonout:
            jsonout.write(
                json.dumps(value, cls=OneWaySafeJSONEncoder)
            )
            jsonout.flush()

            self._execute(
                'import',
                jsonout.name,
            )

            _, task = self.get_task(uuid=value['uuid'])

            return task

    def _get_task_objects(self, obj, *args):
        results = super(TaskwarriorClient, self)._get_task_objects(obj, *args)
        # In `_get_task_object` below, we'll be returning `None` for
        # tasks we couldn't parse properly.  Let's strip those from results.
        return [r for r in results if r is not None]

    def _get_task_object(self, obj):
        try:
            return super(TaskwarriorClient, self)._get_task_object(obj)
        except ValueError as e:
            logger.warning(
                "An error was encountered while parsing task {uuid} "
                "in repository {repo}; omitting task in results: "
                "{message}".format(
                    uuid=str(obj.get('uuid', '??')),
                    message=str(e),
                    repo=str(self.store),
                )
            )
            if self.store:
                self.store.log_error(
                    "An error was encountered while parsing task "
                    "{uuid}; it was omitted from results as a result: "
                    "{message}.".format(
                        uuid=str(obj.get('uuid', '??')),
                        message=str(e),
                    )
                )

            return None
