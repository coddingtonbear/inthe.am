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
        print "Starting ember..."
        fnull = open(os.devnull, 'w')

        ember = threading.Thread(
            target=self.run_ember,
            #kwargs={
            #    'stdout': subprocess.PIPE,
            #    'stderr': subprocess.STDOUT
            #}
        )
        ember.daemon = True
        ember.start()

        print "Waiting for ember server to be available..."
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        started = time.time()
        connected = False
        while time.time() < started + 60:
            result = s.connect_ex(('127.0.0.1', 8000, ))
            if result == 0:
                s.close()
                connected = True
                break
            time.sleep(1)

        if not connected:
            sys.exit(1)
        print "Starting tests..."

        test_args = []
        if kwargs['wip']:
            test_args.append('--behave_wip')

        try:
            result = self.run_tests(*test_args)
        except:
            result = 1
        self.teardown()
        sys.exit(result)
