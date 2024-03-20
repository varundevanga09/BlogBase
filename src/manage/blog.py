from ..db_handler import get_blog_list, get_blog, create_blog, edit_blog, delete_blog


def manage_blog_handler(user_id):
    blogs = get_blog_list(user_id)
    return [{'id': i[0], 'title': i[1]} for i in blogs]


def create_blog_handler(user_id, title, description):
    create_blog(user_id, title, description)


def get_edit_blog_handler(user_id, blog_id):
    blog = get_blog(user_id, blog_id)
    url = f'/manage/blog/edit/{blog_id}'
    return url, {'title': blog[0], 'description': blog[1]}


def post_edit_blog_handler(user_id, blog_id, title, description):
    edit_blog(user_id, blog_id, title, description)


def delete_blog_handler(user_id, blog_id):
    delete_blog(user_id, blog_id)
