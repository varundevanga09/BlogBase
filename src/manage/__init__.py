def _format_input_tags(tags_str: str):
    return [t.capitalize() for t in tags_str.split(',')[:3]]


def _check_update_tags(original_tags: [str], update_tags: [str]):
    added_update_tags = []
    deleted_original_tags = []

    # check deleted tags
    for o in original_tags:
        if o not in update_tags:
            deleted_original_tags.append(o)

    # check added tags
    for u in update_tags:
        if u not in original_tags:
            added_update_tags.append(u)

    return added_update_tags, deleted_original_tags
