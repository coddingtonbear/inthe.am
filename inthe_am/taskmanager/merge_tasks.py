def merge_tasks(alpha, beta):
    merged_from = alpha.get('intheammergedfrom', '')
    if merged_from:
        merged_from = merged_from.split(',')
    else:
        merged_from = []
    merged_from.append(str(beta.get('uuid')))
    alpha['intheammergedfrom'] = ','.join(merged_from)

    for task in alpha, beta:
        if 'annotations' not in task:
            task['annotations'] = []

    original_annotations = alpha.get('annotations')
    original_annotations.extend(beta.get('annotations'))

    if 'annotations' not in beta:
        beta['annotations'] = []
    beta['annotations'].append(
        "This task has been merged with another task. "
        "See {uuid}.".format(
            uuid=alpha.get('uuid')
        )
    )
    beta['intheamduplicateof'] = str(alpha.get('uuid'))
    alpha['annotations'] = original_annotations

    return alpha, beta
