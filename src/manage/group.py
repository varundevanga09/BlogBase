from ..db_handler import get_group_list_by_user_id, get_group_profile, join_group, leave_group


def manage_group_list_handler(user_id):
    groups = get_group_list_by_user_id(user_id)
    return {'groups': [{'id': i[0], 'name': i[1], 'owner_id': i[2]} for i in groups]}


def manage_group_profile_handler(group_id, user_id):
    group_info, members, articles, group_articles = get_group_profile(group_id)
    result = {
        'group_id': group_id,
        'group_name': group_info[0],
        'members': [{'id': i[0], 'name': i[1]} for i in members],
        'is_member': __is_member(user_id, members),
        'latest_posts': [{'blog_id': i[0], 'post_id': i[1], 'title': i[2], 'author': i[3]} for i in articles],
        'member_only_posts': [{'blog_id': i[0], 'post_id': i[1], 'title': i[2], 'author': i[3]} for i in
                              group_articles],
    }
    return result


def join_group_handler(group_id, user_id):
    join_group(group_id, user_id)


def leave_group_handler(group_id, user_id):
    leave_group(group_id, user_id)


def __is_member(user_id, members):
    ids = [str(i[0]) for i in members]
    return user_id in ids
