import os
import subprocess
import sys
import threading
import time

from .run import Command as RunserverCommand


class Command(RunserverCommand):
    def run_tests(self):
        env = os.environ.copy()
        env['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8001'

        return subprocess.call(
            [
                'python',
                'manage.py',
                'test',
                'taskmanager',
            ],
            env=env,
        )

    def handle(self, *args, **kwargs):
        fnull = open(os.devnull, 'w')

        ember = threading.Thread(
            target=self.run_ember,
            #kwargs={
            #    'stdout': fnull,
            #    'stderr': subprocess.STDOUT
            #}
        )
        ember.daemon = True
        ember.start()

        time.sleep(10)

        sys.exit(self.run_tests())
