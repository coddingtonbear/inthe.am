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

    def run_ember(self):
        subprocess.call(
            [
                'ember',
                'server',
            ],
        )

    def handle(self, *args, **kwargs):
        print "\033[31m Note: It will take approximately 30 seconds for both"
        print "      necessary servers to start.  Once you see the"
        print "      message '\033[32mBuild Successful\033[31m', both"
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
