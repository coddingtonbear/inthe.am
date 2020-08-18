import os
from optparse import make_option
import socket
import subprocess
import sys
import tempfile
import threading
import time

from .run import Command as RunserverCommand


class Command(RunserverCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--wip",
            action="store_true",
            dest="wip",
            default=False,
            help="Run only tests marked with @wip",
        )
        parser.add_argument(
            "-x",
            "--failfast",
            action="store_true",
            dest="stop",
            default=False,
            help="Stop running tests at first failure",
        )

    def run_tests(self, *args):
        env = os.environ.copy()
        env["DJANGO_LIVE_TEST_SERVER_ADDRESS"] = "localhost:8001"

        command = [
            "python",
            "manage.py",
            "test",
            "inthe_am.taskmanager",
        ]
        command.extend(args)

        return subprocess.call(command, env=env)

    def handle(self, *args, **kwargs):
        with tempfile.NamedTemporaryFile(
            prefix="ember", suffix=".log", delete=False
        ) as out:
            ember = threading.Thread(
                target=self.run_ember, kwargs={"stdout": out, "stderr": out}
            )
            ember.daemon = True
            ember.start()

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            started = time.time()
            connected = False
            while time.time() < started + 60:
                result = s.connect_ex(("127.0.0.1", 8000,))
                if result == 0:
                    s.close()
                    connected = True
                    break
                time.sleep(1)

            if not connected:
                print "Ember server did not start!"
                out.seek(0)
                print out.read()
                sys.exit(1)

            test_args = list(args)
            if kwargs["wip"]:
                test_args.append("--behave_wip")
            if kwargs["stop"]:
                test_args.append("--behave_stop")

            try:
                result = self.run_tests(*test_args)
            except:
                result = 1
        self.teardown()
        sys.exit(result)
