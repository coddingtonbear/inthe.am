def merge_tasks(alpha, beta):
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


def find_duplicate_tasks(store, task):
    tasks = store.client.filter_tasks({
        'status': 'pending',
        'parent': task['parent'],
        'imask': task['imask'],
        'uuid.not': task['uuid'],
    })

    return {task['uuid'] for task in tasks}
