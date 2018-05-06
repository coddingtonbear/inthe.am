from __future__ import print_function, unicode_literals

import datetime
import json

import progressbar

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q

from inthe_am.taskmanager.models import TaskStore, TaskStoreStatistic
from inthe_am.taskmanager.lock import (
    get_lock_name_for_store,
    get_lock_redis,
    redis_lock,
)


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
                'update_statistics',
                'gc_large_repos',
                'squash',
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
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '--repack-size',
            type=int,
            default=int(1e8)
        )

    def handle(self, *args, **options):
        subcommand = options['subcommand'][0]
        username = options['username']
        minutes = options['minutes']
        repack_size = options['repack_size']

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
        elif subcommand == 'gc_large_repos':
            for store in TaskStore.objects.order_by('-last_synced'):
                try:
                    last_size_measurement = store.statistics.filter(
                        measure=TaskStoreStatistic.MEASURE_SIZE
                    ).latest('created')
                except TaskStoreStatistic.DoesNotExist:
                    continue
                if last_size_measurement.value > repack_size:
                    print("> Repacking {store}...".format(store=store))
                    results = store.gc()
                    print(json.dumps(results, sort_keys=True, indent=4))
                    final_size = store.get_repository_size()
                    print(
                        ">> {diff} MB recovered".format(
                            diff=int(
                                (last_size_measurement.value - final_size)
                                / 1e6
                            )
                        )
                    )
        elif subcommand == 'squash':
            store = TaskStore.objects.get(user__username=username)
            lock_name = get_lock_name_for_store(store)

            starting_size = store.get_repository_size()

            with redis_lock(
                lock_name,
                message='Squash',
                lock_timeout=60*60,
                wait_timeout=60,
            ):
                if (
                    store.trello_local_head
                    and store.trello_local_head != store.repository.head()
                    and not options['force']
                ):
                    raise ValueError("Trello head out-of-date; aborting!")

                head_commit, _ = store._git_command(
                    'rev-list',
                    '--max-parents=0',
                    'HEAD',
                ).communicate()
                head_commit = head_commit.strip()

                store._git_command(
                    'reset',
                    '--soft',
                    head_commit,
                ).communicate()

                store.create_git_checkpoint("Repository squashed.")

                if store.trello_local_head:
                    store.trello_local_head = store.repository.head()
                    store.save()

                results = store.gc()
                ending_size = store.get_repository_size()

                print(
                    ">> {diff} MB recovered".format(
                        diff=int(
                            (starting_size - ending_size)
                            / 1e6
                        )
                    )
                )
