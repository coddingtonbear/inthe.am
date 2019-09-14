import datetime
import json
import logging
import time
import pytz
import re
import subprocess
import select
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now

from inthe_am.taskmanager.lock import get_lock_redis


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    NO_RECENT_MESSAGES = 11

    PREFIX_RE = re.compile(
        r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\d+)\] (.*)$'
    )
    LINE_RES = (
        re.compile(
            r"'(?P<action>[^']+)' from '(?P<username>[^']+)' using "
            r"'(?P<client>[^']+)' at (?P<ip>[0-9.]+):(?P<port__int>[0-9]+)"
        ),
        re.compile(
            r"Client key '(?P<client_key>[^']+)' \d+",
        ),
        re.compile(
            r"Loaded (?P<record_count__int>\d+) records",
        ),
        re.compile(
            r"Branch point: (?P<branch_point>[a-f0-9-]+) --> "
            r"(?P<branch_record_count__int>\d+)",
        ),
        re.compile(
            r"Subset (?P<delta_count__int>\d+) tasks",
        ),
        re.compile(
            r"Stored (?P<stored_count__int>\d+) tasks, "
            r"merged (?P<merged_count__int>\d+) tasks"
        ),
        re.compile(
            r"Serviced in (?P<service_duration__float>[0-9.]+)s"
        )
    )
    TRANSFORMATION_SUFFIXES = {
        '__int': int,
        '__float': float,
    }

    def get_redis_connection(self):
        if not hasattr(self, '_redis'):
            self._redis = get_lock_redis()

        return self._redis

    def operation_is_complete(self, operation):
        if 'service_duration' in operation and 'username' in operation:
            return True
        return False

    def emit_operation_message(self, message):
        r = self.get_redis_connection()
        serialized = json.dumps(
            message,
            cls=DjangoJSONEncoder
        )
        logger.info(
            "Emitting sync notification for %s",
            message.get('username')
        )
        self.last_message_emitted = now()
        r.publish(
            self._get_queue_name(message['username']),
            serialized
        )

    def _get_queue_name(self, username):
        group, username = username.split('/')
        return 'sync.%s' % username

    def process_line(self, line):
        matched = self.PREFIX_RE.match(line)
        if not matched:
            return

        operation_date_string, operation_number_string, message = (
            matched.groups()
        )
        operation_date = datetime.datetime.strptime(
            operation_date_string,
            '%Y-%m-%d %H:%M:%S',
        ).replace(tzinfo=pytz.utc)
        operation_number = int(operation_number_string)

        # If we're back at zero, reset messages -- the remaining ones
        # will never be completed.
        if operation_number < self.highest_message:
            logger.debug(
                "Operation number has been reset; "
                "clearing queued message parts: %s",
                self.operations
            )
            self.operations = {}
            self.highest_message = -1
        if operation_number > self.highest_message:
            self.highest_message = operation_number

        # Create a starting dict for this received message if we haven't
        # seen it before.
        if operation_number in self.operations:
            operation = self.operations[operation_number]
        else:
            operation = {
                'start': operation_date,
            }

        for regex in self.LINE_RES:
            does_match = regex.match(message)
            if does_match:
                result_dict = does_match.groupdict()

                # Transform marked dictionary keys using registered
                # transformation operations.
                for key, value in result_dict.copy().items():
                    for suffix, fn in self.TRANSFORMATION_SUFFIXES.items():
                        if key.endswith(suffix):
                            del result_dict[key]
                            result_dict[key[:-len(suffix)]] = fn(value)
                operation.update(result_dict)
                break

        if self.operation_is_complete(operation):
            self.emit_operation_message(operation)
            del self.operations[operation_number]
        else:
            self.operations[operation_number] = operation

    def get_file_inode(self, filename):
        inode = subprocess.check_output(
            [
                'ls',
                '-i',
                filename,
            ]
        )
        return inode.strip().split(' ')[0]

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='?', type=str)

    def handle(self, *args, **options):
        self.last_message_emitted = None
        self.operations = {}
        self.highest_message = 0

        starting_inode = self.get_file_inode(options['file_path'])
        proc = subprocess.Popen(
            [
                'tail',
                '--max-unchanged-stats=5',
                '-F',
                options['file_path'],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        poller = select.poll()
        poller.register(proc.stdout)

        try:
            while True:
                if poller.poll(1):
                    line = proc.stdout.readline()
                    try:
                        self.process_line(line)
                    except:
                        logger.exception(
                            "An error was encountered while processing the "
                            "logger line %s.",
                            line,
                        )
                else:
                    time.sleep(0.1)

                if (
                    self.last_message_emitted and
                    (
                        (now() - self.last_message_emitted) >
                        datetime.timedelta(
                            seconds=settings.SYNC_LISTENER_WARNING_TIMEOUT
                        )
                    )
                ):
                    current_inode = self.get_file_inode(args[0])
                    logger.error(
                        "No messages have been emitted during the last %s "
                        "minutes; it is likely that something has gone awry "
                        "with our tail.  Original inode: %s; current: %s. "
                        "Exiting; will be restarted automatically.",
                        round(
                            (now() - self.last_message_emitted).seconds / 60.0
                        ),
                        starting_inode,
                        current_inode,
                    )
                    sys.exit(self.NO_RECENT_MESSAGES)
        except Exception as e:
            logger.exception('Fatal error encountered: %s', e)
