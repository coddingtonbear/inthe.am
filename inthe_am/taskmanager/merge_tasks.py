def merge_task_data(alpha, beta):
    for task in alpha, beta:
        merged_from = task.get('intheammergedfrom', '')
        if merged_from:
            merged_from = set(merged_from.split(','))
        else:
            merged_from = set([])

        if 'annotations' not in task:
            task['annotations'] = []

    merged_from.add(str(beta.get('uuid')))
    alpha['intheammergedfrom'] = ','.join(merged_from)

    original_annotations = alpha.get('annotations')
    original_annotations.extend(beta.get('annotations'))
    alpha['annotations'] = original_annotations

    ignore = [
        'annotations',
        'end',
        'entry',
        'id',
        'modified',
        'urgency',
        'uuid',
    ]
    unsalvageable = {}
    for field in beta.keys():
        if field in ignore:
            pass
        elif field not in alpha:
            alpha[field] = beta[field]
        elif alpha[field] != beta[field]:
            unsalvageable[field] = beta[field]

    message = "Task %s merged." % beta['uuid']
    if unsalvageable:
        extra_data = '\n'.join(
            # Note -- two trailing spaces to trigger a newline insertion.
            ["%s: %s  " % (k, v) for k, v in unsalvageable.items()]
        )
        message = message + '\nExtra fields:\n' + extra_data
    alpha['annotations'].append(message)
    beta['annotations'].append(
        "This task has been merged with another task. "
        "See {uuid}.".format(
            uuid=alpha.get('uuid')
        )
    )
    beta['intheamduplicateof'] = str(alpha.get('uuid'))

    return alpha, beta


def find_all_duplicate_tasks(store):
    tasks = store.client.filter_tasks({
        'or': [
            ('status', 'pending', ),
            ('status', 'waiting', ),
        ],
        'parent.not': '',
    })

    all_tasks_by_imask = {}
    for task in tasks:
        all_tasks_by_imask.setdefault(task['parent'], {})\
            .setdefault(task['imask'], set()).add(task['uuid'])

    duplicates = []
    for parent, imask_data in all_tasks_by_imask.items():
        for imask, task_list in imask_data.items():
            if len(task_list) > 1:
                duplicates.append(task_list)

    return duplicates


def merge_all_duplicate_tasks(store, duplicates=None):
    if duplicates is None:
        duplicates = find_all_duplicate_tasks(store)
    else:
        duplicates = [duplicates]

    merged = {}
    for duplicate in duplicates:
        first_task = None
        other_tasks = []

        for task_id in duplicate:
            task = store.client.filter_tasks({'uuid': task_id})[0]
            if (
                first_task is None or
                task['entry'] < first_task['entry'] or
                (
                    task['entry'] == first_task['entry'] and
                    task['id'] < first_task['id']
                )
            ):
                if first_task is not None:
                    other_tasks.append(first_task)
                first_task = task
            else:
                other_tasks.append(task)

        merged_other = []
        for other_task in other_tasks:
            first_task, right = merge_task_data(first_task, other_task)
            merged_other.append(right)

        store.client.task_update(first_task)
        for task in merged_other:
            store.client.task_update(task)
            store.client.task_delete(uuid=task['uuid'])

        merged[first_task['uuid']] = {m['uuid'] for m in merged_other}

    return merged


def find_duplicate_tasks(store, task):
    tasks = store.client.filter_tasks({
        'or': [
            ('status', 'pending', ),
            ('status', 'waiting', ),
        ],
        'parent': task['parent'],
        'imask': task['imask'],
        'uuid.not': task['uuid'],
    })

    return {task['uuid'] for task in tasks}


def merge_duplicate_tasks(store, task):
    duplicate_tasks = find_duplicate_tasks(store, task)
    duplicate_tasks.add(task['uuid'])

    merge_all_duplicate_tasks(store, duplicates=duplicate_tasks)
