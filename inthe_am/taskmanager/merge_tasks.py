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
