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
        'status': 'pending',
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


def merge_all_duplicate_tasks(store):
    for duplicate in find_all_duplicate_tasks(store):
        first_task = None
        other_tasks = []

        for task_id in duplicate:
            task = store.client.filter_tasks({'uuid': task_id})[0]
            if first_task is None or task['entry'] < first_task['entry']:
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


def find_duplicate_tasks(store, task):
    tasks = store.client.filter_tasks({
        'status': 'pending',
        'parent': task['parent'],
        'imask': task['imask'],
        'uuid.not': task['uuid'],
    })

    return {task['uuid'] for task in tasks}
