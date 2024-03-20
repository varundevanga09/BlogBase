from flask import Flask, request, redirect, url_for, render_template
from flask_login import current_user, login_required, LoginManager, UserMixin, login_user, logout_user
from .login.loginHandler import login_handler, add_login_history, create_account_handler, \
    InvalidLoginInformationException
from .login.loginHistoryHandler import view_login_history_handler
from .manage.blog import manage_blog_handler, create_blog_handler, get_edit_blog_handler, post_edit_blog_handler, \
    delete_blog_handler
from .manage.article import manage_article_handler, get_edit_article_handler, post_edit_article_handler, \
    post_create_article_handler, delete_article_handler, get_create_article_handler, BlogNotAuthorizedException
from .manage.view import view_blog_handler, view_article_handler, add_comment_handler, \
    NoPermissionToViewArticleException, home_handler
from .manage.friend import get_friend_list_handler, add_friend_handler, approve_friend_handler, delete_friend_handler
from .manage.group import manage_group_list_handler, manage_group_profile_handler, join_group_handler, \
    leave_group_handler
from .manage.profile import get_settings_handler, post_settings_handler, get_user_profile
from .settings import FLASK_SECRET_KEY
from mysql.connector.errors import IntegrityError
from .db_handler import get_username, like_post, unlike_post, get_user_favorite_posts

api = Flask(__name__)
api.secret_key = FLASK_SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(api)


##### login #################################################################

class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@api.before_request
def require_login():
    if not current_user.is_authenticated and request.endpoint not in ['login', 'create_account']:
        return redirect(url_for('login'))


@api.route('/login/create_account', methods=['POST'])
def create_account():
    username = request.form['new_username']
    password = request.form['new_password']

    try:
        user_id = create_account_handler(username, password)
    except IntegrityError:
        return "The same user name already exists. Please enter a different name."
    # create session
    user = User(user_id)
    login_user(user)

    ip_address = request.remote_addr
    add_login_history(user_id, ip_address)

    return redirect(url_for('home'))


@api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user_id = login_handler(username, password)
        except InvalidLoginInformationException:
            return "Invalid username or password"

        # create session
        user = User(user_id)
        login_user(user)

        ip_address = request.remote_addr
        add_login_history(user_id, ip_address)

        return redirect(url_for('home'))
    else:  # 'GET'
        return render_template('login.html')


@api.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


##### login #################################################################

##### home #################################################################
@api.route('/')
@login_required
def home():
    user_id = current_user.get_id()
    articles, notifications = home_handler(user_id)
    return render_template('home.html',
                           username=get_username(user_id),
                           articles=articles,
                           notifications=notifications,
                           )


##### blog #################################################################
@api.route('/manage/blog')
@login_required
def manage_blogs():
    return render_template('manage_blogs.html', blogs=manage_blog_handler(current_user.get_id()))


@api.route('/manage/blog/create', methods=['POST', 'GET'])
@login_required
def create_blog():
    if request.method == 'GET':
        return render_template('create_edit_blog.html')
    elif request.method == 'POST':
        create_blog_handler(current_user.get_id(), request.form['title'], request.form['description'])
        return redirect(url_for('manage_blogs'))


@api.route('/manage/blog/edit/<blog_id>', methods=['POST', 'GET'])
@login_required
def edit_blog(blog_id):
    user_id = current_user.get_id()
    if request.method == 'GET':
        url, blog = get_edit_blog_handler(user_id, blog_id)
        return render_template('create_edit_blog.html', url=url, blog=blog)
    elif request.method == 'POST':
        post_edit_blog_handler(user_id, blog_id, request.form['title'], request.form['description'])
        return redirect(url_for('manage_blogs'))


@api.route('/manage/blog/delete/<blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    delete_blog_handler(current_user.get_id(), blog_id)
    return redirect(url_for('manage_blogs'))


##### article #################################################################
@api.route('/manage/<blog_id>/articles')
@login_required
def manage_articles(blog_id):
    try:
        articles = manage_article_handler(current_user.get_id(), blog_id)
    except BlogNotAuthorizedException as e:
        return e.msg
    return render_template('manage_articles.html', blog_id=blog_id, articles=articles)


@api.route('/manage/article/create', methods=['POST', 'GET'])
@login_required
def create_article():
    user_id = current_user.get_id()
    if request.method == 'GET':
        blog_id = request.args.get('blog_id', default=None, type=int)
        try:
            blog_name = get_create_article_handler(user_id, blog_id)
        except BlogNotAuthorizedException as e:
            return e.msg
        return render_template('create_edit_article.html', blog_id=blog_id, blog_name=blog_name)
    elif request.method == 'POST':
        blog_id = request.form['blog_id']
        title = request.form['title']
        content = request.form['content']
        visibility = request.form['visibility']
        tags = request.form['posttags']
        try:
            article_id = post_create_article_handler(user_id, blog_id, title, content, visibility, tags)
            return redirect(url_for('view_article', blog_id=blog_id, article_id=article_id))

        except BlogNotAuthorizedException as e:
            return e.msg


@api.route('/manage/article/edit/<blog_id>/<article_id>', methods=['POST', 'GET'])
@login_required
def edit_article(blog_id, article_id):
    user_id = current_user.get_id()
    if request.method == 'GET':
        try:
            article = get_edit_article_handler(user_id, blog_id, article_id)
        except BlogNotAuthorizedException as e:
            return e.msg
        return render_template('create_edit_article.html', **article)
    elif request.method == 'POST':
        article_id = request.form['article_id']
        blog_id = request.form['blog_id']
        title = request.form['title']
        content = request.form['content']
        visibility = request.form['visibility']
        tags = request.form['posttags']
        try:
            post_edit_article_handler(user_id, blog_id, article_id, title, content, visibility, tags)
        except BlogNotAuthorizedException as e:
            return e.msg
        return redirect(url_for('manage_articles', blog_id=blog_id))


@api.route('/manage/article/delete/<blog_id>/<article_id>', methods=['POST'])
@login_required
def delete_article(blog_id, article_id):
    try:
        delete_article_handler(current_user.get_id(), blog_id, article_id)
    except BlogNotAuthorizedException as e:
        return e.msg
    return redirect(url_for('manage_articles', blog_id=blog_id))


##### view #################################################################
@api.route('/view/blog/<blog_id>')
@login_required
def view_blog(blog_id):
    return render_template('view_blog.html', **view_blog_handler(current_user.get_id(), blog_id))


@api.route('/view/article/<blog_id>/<article_id>')
@login_required
def view_article(blog_id, article_id):
    try:
        return render_template('view_article.html', **view_article_handler(current_user.get_id(), blog_id, article_id))
    except NoPermissionToViewArticleException as e:
        return e.msg


##### comment #################################################################
@api.route('/comment/<blog_id>/<article_id>', methods=['POST'])
@login_required
def add_comment(blog_id, article_id):
    comment_text = request.form['comment']
    add_comment_handler(current_user.get_id(), article_id, comment_text)
    return redirect(url_for('view_article', blog_id=blog_id, article_id=article_id))


##### friend #################################################################
@api.route('/friends')
@login_required
def friends_list():
    return render_template('friends_list.html', **get_friend_list_handler(current_user.get_id()))


@api.route('/friend/add/<friend_user_id>')
@login_required
def add_friend(friend_user_id):
    add_friend_handler(current_user.get_id(), friend_user_id)
    return redirect(url_for('friends_list'))


@api.route('/friend/approve/<friend_user_id>', methods=['POST'])
@login_required
def approve_friend(friend_user_id):
    approve_friend_handler(current_user.get_id(), friend_user_id)
    return redirect(url_for('friends_list'))


@api.route('/friend/delete/<friend_user_id>', methods=['POST'])
@login_required
def delete_friend(friend_user_id):
    delete_friend_handler(current_user.get_id(), friend_user_id)
    return redirect(url_for('friends_list'))


##### group #################################################################
@api.route('/groups')
@login_required
def groups_list():
    return render_template('groups_list.html', **manage_group_list_handler(current_user.get_id()))


@api.route('/group_profile/<group_id>')
@login_required
def group_profile(group_id):
    return render_template('group_profile.html', **manage_group_profile_handler(group_id, current_user.get_id()))


@api.route('/group/join/<group_id>', methods=['POST'])
@login_required
def join_group(group_id):
    join_group_handler(group_id, current_user.get_id())
    return redirect(url_for('group_profile', group_id=group_id))


@api.route('/group/leave/<group_id>', methods=['POST'])
@login_required
def leave_group(group_id):
    leave_group_handler(group_id, current_user.get_id())
    return redirect(url_for('group_profile', group_id=group_id))


##### profile #################################################################
@api.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    user_id = current_user.get_id()
    if request.method == 'POST':
        bio = request.form['bio']
        birthday = request.form['birthday']
        interest_tags = request.form['interest_tags']
        post_settings_handler(user_id, bio, birthday, interest_tags)
        return redirect(url_for('user_profile', user_id=user_id))
    else:
        return render_template('settings.html', **get_settings_handler(user_id))


@api.route('/user_profile/<user_id>')
@login_required
def user_profile(user_id):
    return render_template('user_profile.html', **get_user_profile(user_id, current_user.get_id()))


##### login history #################################################################
@api.route('/login_history')
@login_required
def login_history():
    return render_template('login_history.html', records=view_login_history_handler(current_user.get_id()))


##### favorite #################################################################

@api.route('/favorite')
@login_required
def favorite_posts():
    # Fetch liked posts for the current user
    user_id = current_user.get_id()
    user_favorite_posts = get_user_favorite_posts(user_id)
    articles = [{'title': i[5], 'author': i[6], 'blog_id': i[3], 'post_id': i[2]} for i in user_favorite_posts]
    print(user_favorite_posts)
    return render_template('favorite.html', articles=articles)


@api.route('/favorite/delete/<article_id>', methods=['POST'])
@login_required
def delete_favorite(article_id):
    # Delete article from the user's liked posts
    user_id = current_user.get_id()
    unlike_post(article_id, user_id)
    return redirect(url_for('favorite_posts'))


@api.route('/favorite/add/<article_id>', methods=['POST'])
@login_required
def add_favorite(article_id):
    # Add article to the user's liked posts
    user_id = current_user.get_id()
    like_post(article_id, user_id)
    return redirect(url_for('favorite_posts'))


################################################################################

@api.errorhandler(400)
@api.errorhandler(500)
def error_handler(error):
    return 'error'


@api.errorhandler(404)
def error_handler(error):
    return '404 not found'
