from ..db_handler import get_articles_by_blog_id, get_view_permission, get_blog, get_username, get_blog_owner, \
    get_article, get_comment_by_article_id, create_comment, get_latest_articles, get_notifications


def view_blog_handler(user_id, blog_id):
    blog_owner_user_id = get_blog_owner(blog_id)
    blog = get_blog(blog_owner_user_id, blog_id)
    articles = get_articles_by_blog_id(blog_id)
    username = get_username(blog_owner_user_id)
    can_view_friend_post, can_view_group_post, can_view_own_post = get_view_permission(user_id, blog_id)

    format_articles = []
    for a in articles:
        visibility = a[4]
        if not _is_visible(visibility, can_view_friend_post, can_view_group_post, can_view_own_post):
            continue
        format_articles.append({
            "id": a[0],
            "title": a[1],
            "updated_date": a[3],
            "comment_count": a[6],
            "favorite_count": a[7]
        })

    args = {"blog_title": blog[0], "blog_description": blog[1], "articles": format_articles,
            "user_id": blog_owner_user_id, "username": username, "blog_id": blog_id}
    return args


def view_article_handler(user_id, blog_id, article_id):
    article, tags = get_article(blog_id, article_id)
    can_view_friend_post, can_view_group_post, can_view_own_post = get_view_permission(user_id, blog_id)

    # no permission
    if not _is_visible(article[4], can_view_friend_post, can_view_group_post, can_view_own_post):
        raise NoPermissionToViewArticleException

    blog_owner_user_id = get_blog_owner(blog_id)
    blog = get_blog(blog_owner_user_id, blog_id)
    username = get_username(blog_owner_user_id)
    comments = get_comment_by_article_id(article_id)
    format_comments = [{
        "user_id": c[3],
        "username": c[4],
        "text": c[1],
        "date": c[2]
    } for c in comments]

    args = {
        "blog_title": blog[0],
        "article_title": article[0],
        "create_date": article[5],
        "updated_date": article[3],
        "user_id": blog_owner_user_id,
        "username": username,
        "visibility": article[4],
        "content": article[1],
        "blog_id": blog_id,
        "comments": format_comments,
        "article_id": article_id
    }
    return args


def _is_visible(visibility, can_view_friend_post, can_view_group_post, can_view_own_post):
    if visibility == 1:
        return True  # for all
    elif visibility == 2 and can_view_group_post:
        return True  # for group
    elif visibility == 3 and can_view_friend_post:
        return True  # for friend
    elif visibility == 4 and can_view_own_post:
        return True  # for me only
    return False


class NoPermissionToViewArticleException(Exception):
    msg = 'You are not authorized to view this article.'


def add_comment_handler(user_id, article_id, comment_text):
    create_comment(article_id, user_id, comment_text)


def home_handler(user_id):
    articles = get_latest_articles()
    latest_articles = [{
        'blog_id': i[0],
        'post_id': i[1],
        'title': i[2],
        'author': i[3],
        'update_time': i[4],
    } for i in articles]
    notifications = get_notifications(user_id)
    latest_notifications = [{
        'body': i[0],
        'link': i[1],
        'time': i[2],
    } for i in notifications]
    return latest_articles, latest_notifications
