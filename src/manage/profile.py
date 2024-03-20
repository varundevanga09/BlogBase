from ..db_handler import get_settings, get_user_interest, upsert_settings, get_username, get_blog_list, \
    get_friend_list_by_user_id
from ..manage import _format_input_tags, _check_update_tags


def get_settings_handler(user_id):
    profile, tags = get_settings(user_id)
    result = {
        'bio': profile[0] if profile and profile[0] else '',
        'birthday': profile[1] if profile and profile[1] else None,
        'interest_tags': ','.join([i[2] for i in tags]) if tags else '',
        'user_id': user_id,
    }
    return result


def post_settings_handler(user_id, bio, birthday, interest_tags):
    # user_interest_tags check
    update_tags = _format_input_tags(interest_tags)
    original_tags = [i[2] for i in get_user_interest(user_id)]
    added_update_tags, deleted_original_tags = _check_update_tags(original_tags, update_tags)

    # other params
    if birthday == '':
        birthday = None
    upsert_settings(user_id, bio, birthday, added_update_tags, deleted_original_tags)


def get_user_profile(user_id, current_user_id):
    # Fetch basic user info
    user_name = get_username(user_id)

    # Fetch additional user details from UserProfiles
    user_details, tags = get_settings(user_id)
    if user_details is None:
        user_details = ['', '']

    # Fetch user's blogs
    user_blogs = get_blog_list(user_id)
    blogs = [{'id': i[0], 'title': i[1]} for i in user_blogs]

    # Fetch user's friends list and check friendship status (if implemented)
    user_friends = get_friend_list_by_user_id(user_id)
    friends = []
    is_friend = False
    for i in user_friends:
        if i[3] is user_id:
            friends.append({
                'id': i[4],
                'name': i[2],
            })
        else:
            friends.append({
                'id': i[3],
                'name': i[1],
            })
        if i[3] is current_user_id or i[4] is current_user_id:
            is_friend = True

    result = {
        'user_id': user_id,
        'user_name': user_name,
        'bio': user_details[0],
        'birthday': user_details[1],
        'tags': [i[2] for i in tags],
        'friends': friends,
        'is_friend': is_friend,
        'is_me': user_id is current_user_id,
        'blogs': blogs,
    }
    return result
