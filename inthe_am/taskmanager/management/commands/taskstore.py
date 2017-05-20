from __future__ import print_function, unicode_literals

import datetime

import progressbar

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q

from inthe_am.taskmanager.models import TaskStore, TaskStoreStatistic
from inthe_am.taskmanager.lock import get_lock_redis


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'subcommand',
            nargs=1,
            choices=[
                'list',
                'lock',
                'unlock',
                'search',
                'update_statistics'
            ],
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
            users = User.objects.filter(
                Q(email__contains=username) |
                Q(username__contains=username) |
                Q(first_name__contains=username) |
                Q(last_name__contains=username)
            )
            for user in users:
                print(user.username)
        elif subcommand == 'list':
            redis = get_lock_redis()
            for key in redis.keys('*.lock'):
                value = datetime.datetime.fromtimestamp(
                    int(float(redis.get(key)))
                )
                if value > datetime.datetime.utcnow():
                    print('{}: {}'.format(key, value))
        elif subcommand == 'update_statistics':
            run_id = 'update_statistics_{date}'.format(
                date=datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
            )

            with progressbar.ProgressBar(
                max_value=TaskStore.objects.count(),
                widgets=[
                    ' [', progressbar.Timer(), '] ',
                    progressbar.Bar(),
                    ' (', progressbar.ETA(), ') ',
                ]
            ) as bar:
                for idx, store in enumerate(
                    TaskStore.objects.order_by('-last_synced')
                ):
                    TaskStoreStatistic.objects.create(
                        store=store,
                        measure=TaskStoreStatistic.MEASURE_SIZE,
                        value=store.get_repository_size(),
                        run_id=run_id,
                    )
                    bar.update(idx)
