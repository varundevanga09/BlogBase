from ..db_handler import get_friend_list_by_user_id, add_friend_request, approve_friend_request, delete_friend_request


def get_friend_list_handler(user_id):
    result = get_friend_list_by_user_id(user_id)
    friends = []
    for i in result:
        friend = {'is_approved': i[5], 'is_me': True}
        print(i[3], type(i[3]))
        # Current user is the applicant
        if i[3] == int(user_id):
            friend['name'] = i[2]
            friend['id'] = i[4]
        # Current user is the recipient
        else:
            friend['is_me'] = False
            friend['name'] = i[1]
            friend['id'] = i[3]
        friends.append(friend)
    return {'friends': friends}


def add_friend_handler(user_id, friend_user_id):
    add_friend_request(user_id, friend_user_id)


def approve_friend_handler(user_id, friend_user_id):
    approve_friend_request(user_id, friend_user_id)


def delete_friend_handler(user_id, friend_user_id):
    delete_friend_request(user_id, friend_user_id)
