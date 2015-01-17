import os
from optparse import make_option
import socket
import subprocess
import sys
import threading
import time

from .run import Command as RunserverCommand


class Command(RunserverCommand):
    option_list = RunserverCommand.option_list + (
        make_option(
            '--wip',
            action='store_true',
            dest='wip',
            default=False,
            help='Run only tests marked with @wip'
        ),
    )

    def run_tests(self, *args):
        env = os.environ.copy()
        env['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8001'

        command = [
            'python',
            'manage.py',
            'test',
            'taskmanager',
        ]
        command.extend(args)

        return subprocess.call(command, env=env)

    def handle(self, *args, **kwargs):
        fnull = open(os.devnull, 'w')

        ember = threading.Thread(
            target=self.run_ember,
            kwargs={
                'stdout': fnull,
                'stderr': subprocess.STDOUT
            }
        )
        ember.daemon = True
        ember.start()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            result = s.connect_ex(('127.0.0.1', 8000, ))
            if result == 0:
                s.close()
                break
            time.sleep(1)

        test_args = []
        if kwargs['wip']:
            test_args.append('--behave_wip')

        try:
            result = self.run_tests(*test_args)
        except:
            result = 1
        self.teardown()
        sys.exit(result)
