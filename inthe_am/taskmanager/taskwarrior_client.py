import logging
import subprocess

import six
from taskw import TaskWarriorShellout


logger = logging.getLogger(__name__)


class TaskwarriorClient(TaskWarriorShellout):
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
        return stdout, stderr
