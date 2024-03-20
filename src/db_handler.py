import mysql.connector
from .settings import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME, Visibility


def __create_cursor(db_username, db_password, db_host, db_name):
    cnx = mysql.connector.connect(user=db_username, password=db_password,
                                  host=db_host,
                                  database=db_name)
    cursor = cnx.cursor()
    return cursor, cnx


def __close_cursor(cursor, cnx):
    cnx.commit()
    cursor.close()
    cnx.close()


# login
def create_user(username, password, salt):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)

    args = [username, password, salt, 0]
    result_args = cursor.callproc('CreateUser', args)

    __close_cursor(cursor, cnx)
    new_user_id = result_args[-1]
    return new_user_id


def get_user_from_name(username):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)

    query = "SELECT id, Salt, Password FROM Users WHERE UserName = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    __close_cursor(cursor, cnx)
    return result


def get_username(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)

    query = "SELECT UserName FROM Users WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    __close_cursor(cursor, cnx)
    return result[0]


def create_login_history(user_id, ip_address):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [user_id, ip_address]
    cursor.callproc('AddLoginHistory', args)
    __close_cursor(cursor, cnx)


def get_login_history_by_user_id(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = "SELECT LoginDateTime, LoginIPAddress FROM LoginHistory WHERE UserID = %s LIMIT 10"
    cursor.execute(query, (user_id,))
    history = cursor.fetchall()
    __close_cursor(cursor, cnx)

    return history


# manage blog
def get_blog_list(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = "SELECT id, BlogName FROM Blogs WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    blogs = cursor.fetchall()
    __close_cursor(cursor, cnx)

    return blogs


def get_blog(user_id, blog_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = "SELECT BlogName, Description FROM Blogs WHERE UserID = %s AND id = %s"
    cursor.execute(query, (user_id, blog_id))
    blog = cursor.fetchone()
    __close_cursor(cursor, cnx)

    return blog


def create_blog(user_id, title, description):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [user_id, title, description]
    cursor.callproc('CreateBlog', args)
    __close_cursor(cursor, cnx)


def edit_blog(user_id, blog_id, title, description):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [user_id, blog_id, title, description]
    cursor.callproc('UpdateBlog', args)
    __close_cursor(cursor, cnx)


def delete_blog(user_id, blog_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [user_id, blog_id]
    cursor.callproc('DeleteBlog', args)
    __close_cursor(cursor, cnx)


# manage article
def get_articles_by_blog_id(blog_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = "SELECT * FROM BlogPostsView WHERE BlogID = %s"
    args = [blog_id]
    cursor.execute(query, args)
    articles = cursor.fetchall()
    __close_cursor(cursor, cnx)

    return articles


def get_article(blog_id, article_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = "SELECT Title, Content, PostDate, UpdatedDate, Visibility, UpdatedDate FROM Posts WHERE BlogID = %s AND id = %s;"
    args = [blog_id, article_id]
    cursor.execute(query, args)
    article = cursor.fetchone()
    __close_cursor(cursor, cnx)
    tags = get_post_tags(article_id)

    return article, tags


def create_article(blog_id, title, content, visibility, tags):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [blog_id, title, content, visibility, 0]
    return_args = cursor.callproc('CreatePost', args)
    article_id = return_args[-1]
    for t in tags:
        _create_post_tag(article_id, t, cursor)
    __close_cursor(cursor, cnx)
    return article_id


def edit_article(blog_id, article_id, title, content, visibility, added_update_tags, deleted_original_tags):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [article_id, blog_id, title, content, visibility]
    cursor.callproc('EditPost', args)
    for t in deleted_original_tags:
        _delete_post_tag(article_id, t, cursor)
    for t in added_update_tags:
        _create_post_tag(article_id, t, cursor)
    __close_cursor(cursor, cnx)


def delete_article(blog_id, article_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [article_id, blog_id]
    cursor.callproc('DeletePost', args)
    __close_cursor(cursor, cnx)


def is_user_blog_owner(user_id, blog_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = "SELECT IsUserBlogOwner(%s, %s)"
    args = [user_id, blog_id]
    cursor.execute(query, args)
    result = cursor.fetchone()
    __close_cursor(cursor, cnx)
    return result[0]


def get_post_tags(article_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT * FROM PostTagsView WHERE PostID = %s'
    args = [article_id]
    cursor.execute(query, args)
    result = cursor.fetchall()
    __close_cursor(cursor, cnx)
    return result


def _create_post_tag(article_id, tag, cursor):
    args = [tag, article_id]
    cursor.callproc('GetOrCreateTagForPost', args)


def _delete_post_tag(article_id, tag, cursor):
    args = [tag, article_id]
    cursor.callproc('DeletePostTag', args)


# view
def get_view_permission(user_id, blog_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [user_id, blog_id, False, False, False]
    result_args = cursor.callproc('CanViewPost', args)
    can_view_friend_post = result_args[2]
    can_view_group_post = result_args[3]
    can_view_own_post = result_args[4]
    return can_view_friend_post, can_view_group_post, can_view_own_post


def get_blog_owner(blog_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT UserID FROM Blogs WHERE id = %s'
    args = [blog_id]
    cursor.execute(query, args)
    result = cursor.fetchone()
    __close_cursor(cursor, cnx)
    return result[0]


def get_comment_by_article_id(article_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT * FROM PostCommentsView WHERE PostID = %s'
    args = [article_id]
    cursor.execute(query, args)
    result = cursor.fetchall()
    __close_cursor(cursor, cnx)
    return result


def create_comment(article_id, user_id, comment_text):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    args = [article_id, user_id, comment_text]
    cursor.callproc('InsertComment', args)
    __close_cursor(cursor, cnx)


# Favorite
def get_liked_status(user_id, article_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT Liked FROM FavoritePostsView WHERE UserID = %s AND PostID = %s'
    args = [user_id, article_id]
    cursor.execute(query, args)
    result = cursor.fetchone()
    __close_cursor(cursor, cnx)
    return result[0] if result else False


def like_post(article_id, user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'INSERT INTO FavoritePostsView (PostID, UserID) VALUES (%s, %s)'
    args = [article_id, user_id]
    cursor.execute(query, args)
    __close_cursor(cursor, cnx)


def unlike_post(article_id, user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'DELETE FROM Favorites WHERE PostID = %s AND UserID = %s'
    args = [article_id, user_id]
    cursor.execute(query, args)
    __close_cursor(cursor, cnx)


def get_user_favorite_posts(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT * FROM FavoritePostsView WHERE UserID = %s'


# group
def get_group_list_by_user_id(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT Groups.id, Groups.GroupName, Groups.OwnerID FROM Groups ' \
            'INNER JOIN GroupMembers ON Groups.id = GroupMembers.GroupID WHERE GroupMembers.UserID = %s'
    args = [user_id]
    cursor.execute(query, args)
    result = cursor.fetchall()
    __close_cursor(cursor, cnx)
    return result


def get_group_profile(group_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    # group infomation
    query = 'SELECT Groups.GroupName, Groups.OwnerID FROM Groups WHERE Groups.id = %s'
    args = [group_id]
    cursor.execute(query, args)
    group_info = cursor.fetchone()

    # group member
    query = 'SELECT GroupMembers.UserID, Users.UserName FROM GroupMembers ' \
            'INNER JOIN Users ON GroupMembers.UserID = Users.id WHERE GroupMembers.GroupID = %s'
    cursor.execute(query, args)
    members = cursor.fetchall()

    # latest articles(all)
    query = '''SELECT B.BlogID, B.PostID, B.Title, Users.UserName FROM BlogPostsView B
JOIN Blogs ON B.BlogID = Blogs.id
JOIN Users ON Blogs.UserID = Users.id
JOIN GroupMembers ON Users.id = GroupMembers.UserID
WHERE GroupMembers.GroupID = %s AND B.Visibility = %s
ORDER BY B.UpdatedDate DESC LIMIT 3'''
    args = [group_id, Visibility.VISIBLE_TO_ALL.value]
    cursor.execute(query, args)
    articles = cursor.fetchall()

    # latest articles(group)
    args = [group_id, Visibility.VISIBLE_TO_GROUP.value]
    cursor.execute(query, args)
    group_articles = cursor.fetchall()

    __close_cursor(cursor, cnx)
    return group_info, members, articles, group_articles


def join_group(group_id, user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'INSERT INTO GroupMembers (GroupID, UserID, JoinedDateTime) VALUES (%s, %s, NOW())'
    args = [group_id, user_id]
    cursor.execute(query, args)
    cnx.commit()
    __close_cursor(cursor, cnx)


def leave_group(group_id, user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'DELETE FROM GroupMembers WHERE GroupID = %s AND UserID = %s'
    args = [group_id, user_id]
    cursor.execute(query, args)
    cnx.commit()
    __close_cursor(cursor, cnx)


# friend
def get_friend_list_by_user_id(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = '''SELECT Friends.id,
    Users1.UserName as UserName1,
    Users2.UserName as UserName2,
    Friends.UserID1,
    Friends.UserID2,
    Friends.IsApproved
FROM Friends
JOIN Users as Users1 ON Friends.UserID1 = Users1.id
JOIN Users as Users2 ON Friends.UserID2 = Users2.id
WHERE Users1.id = %s OR Users2.id = %s
'''
    args = [user_id, user_id]
    cursor.execute(query, args)
    result = cursor.fetchall()
    __close_cursor(cursor, cnx)
    return result


def add_friend_request(user_id, friend_user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'INSERT INTO Friends (UserID1, UserID2, IsApproved) VALUES (%s, %s, False)'
    args = [user_id, friend_user_id]
    cursor.execute(query, args)
    __close_cursor(cursor, cnx)


def approve_friend_request(user_id, friend_user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'UPDATE Friends SET IsApproved = True WHERE UserID1 = %s AND UserID2 = %s'
    args = [friend_user_id, user_id]
    cursor.execute(query, args)
    __close_cursor(cursor, cnx)


def delete_friend_request(user_id, friend_user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'DELETE FROM Friends WHERE (UserID1 = %s AND UserID2 = %s) OR (UserID1 = %s AND UserID2 = %s)'
    args = [user_id, friend_user_id, friend_user_id, user_id]
    cursor.execute(query, args)
    __close_cursor(cursor, cnx)


# home
def get_latest_articles():
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT * FROM BlogPostsViewLimited'
    cursor.execute(query)
    result = cursor.fetchall()
    __close_cursor(cursor, cnx)
    return result


def get_notifications(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT Body, Link, CreatedAt FROM Notifications WHERE UserID = %s ORDER BY CreatedAt DESC LIMIT 5'
    cursor.execute(query, [user_id])
    result = cursor.fetchall()
    __close_cursor(cursor, cnx)
    return result


# profile
def get_settings(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = 'SELECT Bio, DOB FROM UserProfiles WHERE UserID = %s'
    args = [user_id]
    cursor.execute(query, args)
    profile = cursor.fetchone()
    __close_cursor(cursor, cnx)

    tags = get_user_interest(user_id)
    return profile, tags


def get_user_interest(user_id):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    query = '''SELECT UserInterests.id, UserInterests.TagID, Tags.TagName
    FROM UserInterests JOIN Tags ON UserInterests.TagID = Tags.id WHERE UserInterests.UserID = %s'''
    args = [user_id]
    cursor.execute(query, args)
    tags = cursor.fetchall()
    __close_cursor(cursor, cnx)
    return tags


def upsert_settings(user_id, bio, dob, added_update_tags, deleted_original_tags):
    cursor, cnx = __create_cursor(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
    try:
        cnx.start_transaction()

        # UserProfiles
        query = 'SELECT id FROM UserProfiles WHERE UserID = %s'
        cursor.execute(query, [user_id])
        profile = cursor.fetchone()

        if profile is None:
            # insert
            query = 'INSERT INTO UserProfiles (UserID, Bio, DOB) VALUES (%s, %s, %s)'
            cursor.execute(query, [user_id, bio, dob])
        else:
            # update
            query = 'UPDATE UserProfiles SET Bio = %s, DOB = %s WHERE UserID = %s'
            cursor.execute(query, [bio, dob, user_id])

        # UserInterest
        for t in deleted_original_tags:
            cursor.callproc('DeleteUserInterest', [t, user_id])
        for t in added_update_tags:
            cursor.callproc('AddUserInterest', [t, user_id])

        cnx.commit()
    except:
        cnx.rollback()
        raise
    finally:
        cursor.close()
        cnx.close()
