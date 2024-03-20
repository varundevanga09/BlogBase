from ..db_handler import is_user_blog_owner, get_articles_by_blog_id, create_article, delete_article, edit_article, \
    get_article, get_blog, get_post_tags
from ..manage import _format_input_tags, _check_update_tags

class BlogNotAuthorizedException(Exception):
    msg = 'You are not authorized to operate this blog.'


def _authorize_blog(func):
    def wrapper(user_id, blog_id, *args, **kwargs):
        if is_user_blog_owner(user_id, blog_id):
            return func(user_id, blog_id, *args, **kwargs)
        else:
            raise BlogNotAuthorizedException

    return wrapper


@_authorize_blog
def manage_article_handler(user_id, blog_id):
    articles = get_articles_by_blog_id(blog_id)
    result = []
    for a in articles:
        result.append({
            "id": a[0],
            "title": a[1],
            "postdate": a[2],
            "updated_date": a[3],
            "visibility": a[4],
            "blog_id": a[5],
            "comment_count": a[6],
            "favorite_count": a[7]
        })
    return result


@_authorize_blog
def get_create_article_handler(user_id, blog_id):
    blog = get_blog(user_id, blog_id)
    blog_name = blog[0]
    return blog_name


@_authorize_blog
def post_create_article_handler(user_id, blog_id, title, content, visibility, tags):
    article_id = create_article(blog_id, title, content, visibility, _format_input_tags(tags))
    return article_id


@_authorize_blog
def get_edit_article_handler(user_id, blog_id, article_id):
    article, tags = get_article(blog_id, article_id)
    blog = get_blog(user_id, blog_id)
    blog_name = blog[0]
    return {"title": article[0], "content": article[1], "postdate": article[2], "updatedDate": article[3],
            "visibility": article[4], "blog_id": blog_id, "article_id": article_id, "blog_name": blog_name,
            "posttags": ",".join([i[3] for i in tags])}


@_authorize_blog
def post_edit_article_handler(user_id, blog_id, article_id, title, content, visibility, tags):
    update_tags = _format_input_tags(tags)
    original_tags = [i[3] for i in get_post_tags(article_id)]
    added_update_tags, deleted_original_tags = _check_update_tags(original_tags, update_tags)
    edit_article(blog_id, article_id, title, content, visibility, added_update_tags, deleted_original_tags)


@_authorize_blog
def delete_article_handler(user_id, blog_id, article_id):
    delete_article(blog_id, article_id)
