from ConfigParser import NoOptionError
import copy

from bugwarrior.config import asbool
from bugwarrior.db import (
    ABORT_PROCESSING,
    build_key_list,
    build_uda_config_overrides,
    find_local_uuid,
    get_managed_task_uuids,
    merge_left,
    MultipleMatches,
    NotFound,
)
from django.conf import settings
from taskw.exceptions import TaskwarriorError

from .taskwarrior_client import TaskwarriorClient


def synchronize(runlog, issue_generator, conf, main_section):
    store = runlog.config.store

    def _bool_option(section, option, default):
        try:
            return section in conf.sections() and \
                asbool(conf.get(section, option, default))
        except NoOptionError:
            return default

    targets = [t.strip() for t in conf.get(main_section, 'targets').split(',')]
    services = set([conf.get(target, 'service') for target in targets])
    key_list = build_key_list(services)
    uda_list = build_uda_config_overrides(services)

    static_fields = ['priority']
    if conf.has_option(main_section, 'static_fields'):
        static_fields = conf.get(main_section, 'static_fields').split(',')

    all_config_overrides = copy.deepcopy(uda_list)
    all_config_overrides['uda'].update(
        settings.TASKWARRIOR_CONFIG_OVERRIDES.get('uda', {})
    )
    tw = TaskwarriorClient(
        store.taskrc.path,
        config_overrides=all_config_overrides,
        store=store,
    )

    legacy_matching = False

    issue_updates = {
        'new': [],
        'existing': [],
        'changed': [],
        'closed': get_managed_task_uuids(tw, key_list, legacy_matching),
    }

    for issue in issue_generator:
        if isinstance(issue, tuple) and issue[0] == ABORT_PROCESSING:
            runlog.add_output(str(issue[1]))
            raise RuntimeError(issue[1])
        try:
            existing_uuid = find_local_uuid(
                tw, key_list, issue, legacy_matching=legacy_matching
            )
            issue_dict = dict(issue)
            _, task = tw.get_task(uuid=existing_uuid)

            # Drop static fields from the upstream issue.  We don't want to
            # overwrite local changes to fields we declare static.
            for field in static_fields:
                del issue_dict[field]

            # Merge annotations & tags from online into our task object
            merge_left('annotations', task, issue_dict, hamming=True)
            merge_left('tags', task, issue_dict)

            issue_dict.pop('annotations', None)
            issue_dict.pop('tags', None)

            task.update(issue_dict)

            if task.get_changes(keep=True):
                issue_updates['changed'].append(task)
            else:
                issue_updates['existing'].append(task)

            if existing_uuid in issue_updates['closed']:
                issue_updates['closed'].remove(existing_uuid)

        except MultipleMatches as e:
            runlog.add_output('Multiple matches: %s' % unicode(e))
        except NotFound:
            issue_updates['new'].append(dict(issue))

    # Add new issues
    runlog.add_output("Adding %s tasks" % len(issue_updates['new']))
    for issue in issue_updates['new']:
        runlog.add_output(
            "Adding task %s" % issue['description'].encode("utf-8"),
        )
        try:
            tw.task_add(**issue)
        except TaskwarriorError as e:
            runlog.add_output(
                "Unable to add task: %s" % e.stderr
            )

    runlog.add_output(
        "Updating %s tasks" % len(issue_updates['changed'])
    )
    for issue in issue_updates['changed']:
        changes = '; '.join([
            '{field}: {f} -> {t}'.format(
                field=field,
                f=repr(ch[0]),
                t=repr(ch[1])
            )
            for field, ch in issue.get_changes(keep=True).items()
        ])
        runlog.add_output(
            "Updating task %s, %s; %s" % (
                unicode(issue['uuid']).encode("utf-8"),
                issue['description'].encode("utf-8"),
                changes,
            )
        )

        try:
            tw.task_update(issue)
        except TaskwarriorError as e:
            runlog.add_output(
                "Unable to modify task: %s" % e.stderr
            )

    runlog.add_output("Closing %s tasks" % len(issue_updates['closed']))
    for issue in issue_updates['closed']:
        _, task_info = tw.get_task(uuid=issue)
        runlog.add_output(
            "Completing task %s %s" % (
                issue,
                task_info.get('description', '').encode('utf-8'),
            )
        )

        try:
            tw.task_done(uuid=issue)
        except TaskwarriorError as e:
            runlog.add_output(
                "Unable to close task: %s" % e.stderr
            )
