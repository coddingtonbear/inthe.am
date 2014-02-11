import curses.ascii
import logging
import subprocess

import six
from taskw import TaskWarriorShellout


logger = logging.getLogger(__name__)


class TaskwarriorError(Exception):
    def __init__(self, stderr, stdout, code):
        self.stderr = stderr.strip()
        self.stdout = stdout.strip()
        self.code = code
        super(TaskwarriorError, self).__init__(self.stderr)


class TaskwarriorClient(TaskWarriorShellout):
    ACCEPTABLE_PROPERTIES = [
        'priority',
        'project',
        'due',
        'wait',
    ]

    def _get_acceptable_prefix(self, command):
        if ' ' in command:
            return command
        if command.lower() in self.ACCEPTABLE_PROPERTIES:
            return command.lower()
        return False

    def _strip_unsafe_args(self, *args):
        final_args = []
        for raw_arg in args:
            arg = self._strip_unsafe_chars(raw_arg)
            if ':' in arg:
                cmd, value = arg.split(':', 1)
                acceptable_cmd = self._get_acceptable_prefix(cmd)
                if acceptable_cmd is False:
                    continue  # Don't add this arg!
                arg = ':'.join(
                    [acceptable_cmd, value]
                )

            final_args.append(arg)

        return final_args

    def _strip_unsafe_chars(self, incoming):
        return ''.join(
            char for char in incoming if curses.ascii.isprint(char)
        )

    def _execute_safe(self, *args):
        return self._execute(
            *self._strip_unsafe_args(*args)
        )

    def _execute(self, *args):
        """ Execute a given taskwarrior command with arguments

        Returns a 2-tuple of stdout and stderr (respectively).

        """
        command = [
            'task',
            'rc:%s' % self.config_filename,
            'rc.json.array=TRUE',
            'rc.verbose=nothing',
            'rc.confirmation=no',
        ] + [six.text_type(arg) for arg in args]
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            logger.error(
                'Non-zero return code returned from taskwarrior: %s' % (
                    proc.returncode
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
        return stdout, stderr
