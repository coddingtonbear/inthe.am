from __future__ import print_function, unicode_literals

import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from inthe_am.taskmanager.models import TaskStore
from inthe_am.taskmanager.lock import get_lock_redis


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'subcommand',
            nargs=1,
            choices=['list', 'lock', 'unlock', 'search'],
            type=str,
        )
        parser.add_argument(
            'username',
            nargs='?',
            type=str
        )
        parser.add_argument(
            '--minutes',
            type=int,
            default=5,
        )

    def handle(self, *args, **options):
        subcommand = options['subcommand'][0]
        username = options['username']
        minutes = options['minutes']

        if subcommand == 'lock':
            store = TaskStore.objects.get(user__username=username)
            store.set_lock_state(lock=True, seconds=minutes*60)
            print('{} locked'.format(store))
        elif subcommand == 'unlock':
            store = TaskStore.objects.get(user__username=username)
            store.set_lock_state(lock=False)
            print('{} unlocked'.format(store))
        elif subcommand == 'search':
            users = User.objects.filter(user__username__contains=username)
            for user in users:
                print(user.username)
        elif subcommand == 'list':
            redis = get_lock_redis()
            for key in redis.keys('*.lock'):
                value = redis.get(key)
                print(
                    '{}: {}'.format(
                        key,
                        datetime.datetime.fromtimestamp(int(value)),
                    )
                )
