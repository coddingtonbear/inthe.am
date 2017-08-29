import os
import signal
import subprocess
import threading
import time

from django.conf import settings
from django.core.management.base import BaseCommand


CONFIG = settings.RUN_LOCALLY


class Command(BaseCommand):
    pids = []

    def run_runserver(self):
        proc = subprocess.Popen(
            [
                CONFIG.get('python_path', '/usr/bin/python'),
                'manage.py',
                'runserver',
                '0.0.0.0:%s' % CONFIG.get('runserver_port', 8001)
            ],
            env=os.environ.copy()
        )
        self.pids.append(proc.pid)
        os.waitpid(proc.pid, 0)

    def run_ember(self, **kwargs):
        kwargs['env'] = os.environ.copy()
        proc = subprocess.Popen(
            [
                CONFIG.get('ember_path', '/usr/bin/ember'),
                'server',
                '--live-reload-port', str(CONFIG.get('ember_port', 8009)),
            ],
            **kwargs
        )
        self.pids.append(proc.pid)
        os.waitpid(proc.pid, 0)

    def teardown(self):
        for pid in self.pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except:
                print "\033[31mFailed to kill PID %s\033[m" % pid

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
            pass
        self.teardown()
