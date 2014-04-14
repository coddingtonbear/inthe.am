import curses.ascii
import logging

from taskw import TaskWarriorShellout

from .task import Task


logger = logging.getLogger(__name__)


class TaskwarriorClient(TaskWarriorShellout):
    def _get_acceptable_properties(self):
        return list(
            set(Task.KNOWN_FIELDS) - set(Task.READ_ONLY_FIELDS)
        ) + ['uuid']

    def _get_acceptable_prefix(self, command):
        if ' ' in command:
            return command
        if command.lower() in self._get_acceptable_properties():
            return command.lower()
        return False

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
            else:
                description_args.append(arg)

        return final_args + ['--'] + description_args

    def _strip_unsafe_chars(self, incoming):
        return ''.join(
            char for char in incoming if curses.ascii.isprint(char)
        )

    def _execute_safe(self, *args):
        return self._execute(
            *self._strip_unsafe_args(*args)
        )
