import datetime
import traceback

import progressbar

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.timezone import now

from inthe_am.taskmanager.models import TaskStore, TaskStoreStatistic
from inthe_am.taskmanager.lock import get_lock_redis


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "subcommand",
            nargs=1,
            choices=[
                "list",
                "lock",
                "unlock",
                "search",
                "update_statistics",
                "gc_large_repos",
                "squash",
                "delete_old_accounts",
                "list_old_accounts",
                "migrate_all",
            ],
            type=str,
        )
        parser.add_argument("username", nargs="?", type=str)
        parser.add_argument(
            "--minutes", type=int, default=5,
        )
        parser.add_argument(
            "--force", action="store_true", default=False,
        )
        parser.add_argument("--repack-size", type=int, default=int(5e7))
        parser.add_argument("--squash-size", type=int, default=int(1e8))
        parser.add_argument("--min-use-recency-days", type=int, default=370)

    def handle(self, *args, **options):
        subcommand = options["subcommand"][0]
        username = options["username"]
        minutes = options["minutes"]
        repack_size = options["repack_size"]
        squash_size = options["squash_size"]
        min_use_recency_days = options["min_use_recency_days"]

        if subcommand == "lock":
            store = TaskStore.objects.get(user__username=username)
            store.set_lock_state(lock=True, seconds=minutes * 60)
            print(f"{store} locked")
        elif subcommand == "unlock":
            store = TaskStore.objects.get(user__username=username)
            store.set_lock_state(lock=False)
            print(f"{store} unlocked")
        elif subcommand == "search":
            users = User.objects.filter(
                Q(email__contains=username)
                | Q(username__contains=username)
                | Q(first_name__contains=username)
                | Q(last_name__contains=username)
            )
            for user in users:
                print(user.username)
        elif subcommand == "list":
            redis = get_lock_redis()
            for key in redis.keys("*.lock"):
                value = datetime.datetime.fromtimestamp(int(float(redis.get(key))))
                if value > datetime.datetime.utcnow():
                    print(f"{key}: {value}")
        elif subcommand == "update_statistics":
            run_id = "update_statistics_{date}".format(
                date=datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
            )
            print(f"Run ID: {run_id}")
            with progressbar.ProgressBar(
                max_value=TaskStore.objects.count(),
                widgets=[
                    " [",
                    progressbar.Timer(),
                    "] ",
                    progressbar.Bar(),
                    " (",
                    progressbar.ETA(),
                    ") ",
                ],
            ) as bar:
                for idx, store in enumerate(TaskStore.objects.order_by("-last_synced")):
                    TaskStoreStatistic.objects.create(
                        store=store,
                        measure=TaskStoreStatistic.MEASURE_SIZE,
                        value=store.get_repository_size(),
                        run_id=run_id,
                    )
                    bar.update(idx)
        elif subcommand == "migrate_all":
            old_path = "/var/www/twweb/task_data/"
            new_path = "/task_data/"
            with progressbar.ProgressBar(
                max_value=TaskStore.objects.count(),
                widgets=[
                    " [",
                    progressbar.Timer(),
                    "] ",
                    progressbar.Bar(),
                    " (",
                    progressbar.ETA(),
                    ") ",
                ],
            ) as bar:
                successful = 0
                total = 0
                for idx, store in enumerate(TaskStore.objects.order_by("-last_synced")):
                    success = True

                    try:
                        success_rate = successful / total * 100
                    except Exception:
                        success_rate = 0

                    store.local_path = store.local_path.replace(old_path, new_path)

                    try:
                        del store._metadata
                    except AttributeError:
                        pass

                    try:
                        del store._taskrc
                    except AttributeError:
                        pass

                    try:
                        for k, v in store.metadata.items():
                            if isinstance(v, str):
                                store.metadata[k] = v.replace(old_path, new_path)
                    except Exception:
                        print(
                            f"Failed to update metadata for {store}: {success_rate}% OK"
                        )
                        success = False

                    try:
                        del store._metadata
                    except AttributeError:
                        pass

                    try:
                        del store._taskrc
                    except AttributeError:
                        pass

                    try:
                        for k, v in store.taskrc.items():
                            store.taskrc[k] = v.replace(old_path, new_path)
                    except Exception:
                        print(
                            f"Failed to update taskrc for {store}: {success_rate}% OK"
                        )
                        success = False

                    try:
                        del store._metadata
                    except AttributeError:
                        pass

                    try:
                        del store._taskrc
                    except AttributeError:
                        pass

                    store.save()

                    if success:
                        successful += 1
                    total += 1

                    bar.update(idx)
        elif subcommand == "gc_large_repos":
            for store in TaskStore.objects.order_by("-last_synced"):
                try:
                    last_size_measurement = store.statistics.filter(
                        measure=TaskStoreStatistic.MEASURE_SIZE
                    ).latest("created")
                except TaskStoreStatistic.DoesNotExist:
                    continue
                if last_size_measurement.value > squash_size:
                    print(f"> Squashing {store}...")
                    try:
                        store.squash()
                        store.gc()
                        final_size = store.get_repository_size()
                        print(
                            ">> {diff} MB recovered".format(
                                diff=int(
                                    (last_size_measurement.value - final_size) / 1e6
                                )
                            )
                        )
                    except Exception as e:
                        print(f"> FAILED: {e}")
                        traceback.print_exc()
                elif last_size_measurement.value > repack_size:
                    print(f"> Repacking {store}...")
                    try:
                        store.gc()
                        final_size = store.get_repository_size()
                        print(
                            ">> {diff} MB recovered".format(
                                diff=int(
                                    (last_size_measurement.value - final_size) / 1e6
                                )
                            )
                        )
                    except Exception as e:
                        print(f"> FAILED: {e}")
                        traceback.print_exc()
        elif subcommand == "squash":
            store = TaskStore.objects.get(user__username=username)

            starting_size = store.get_repository_size()

            store.squash(force=options["force"])
            store.gc()
            ending_size = store.get_repository_size()

            print(f">> {int((starting_size - ending_size) / 1000000.0)} MB recovered")
        elif subcommand == "delete_old_accounts":
            min_action_recency = now() - datetime.timedelta(days=min_use_recency_days)
            for store in TaskStore.objects.filter(
                last_synced__lt=min_action_recency,
                user__last_login__lt=min_action_recency,
            ).order_by("-last_synced"):
                print(f"> Deleting {store.local_path}")
                store.delete()
                store.user.delete()
        elif subcommand == "list_old_accounts":
            min_action_recency = now() - datetime.timedelta(days=min_use_recency_days)
            output_format = "{path}\t{last_synced}\t{last_login}"
            print(
                output_format.format(
                    path="path",
                    last_synced="last_synced",
                    last_login="user__last_login",
                )
            )
            for store in TaskStore.objects.filter(
                last_synced__lt=min_action_recency,
                user__last_login__lt=min_action_recency,
            ).order_by("-last_synced"):
                print(
                    output_format.format(
                        path=store.local_path,
                        last_synced=store.last_synced,
                        last_login=store.user.last_login,
                    )
                )
