import subprocess
import sys
import threading
import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def run_runserver(self):
        subprocess.call(
            [
                'python',
                'manage.py',
                'runserver',
                '0.0.0.0:8001',
            ]
        )

    def run_ember(self, **kwargs):
        subprocess.call(
            [
                'ember',
                'server',
            ],
            **kwargs
        )

    def handle(self, *args, **kwargs):
        print "\033[31m Note: It will take a few seconds for both necessary"
        print "      servers to start.  Once you see the message"
        print "      message '\033[32mBuild Successful\033[31m', both",
        print "servers are up."
        print "\033[m"
        runserver = threading.Thread(target=self.run_runserver)
        runserver.daemon = True
        runserver.start()

        ember = threading.Thread(target=self.run_ember)
        ember.daemon = True
        ember.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit()
