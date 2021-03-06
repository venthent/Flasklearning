from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash, request, current_app, make_response
from Flasklearning.flaskyy.app.main import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from Flasklearning.flaskyy.app import db, models
from flask_login import login_required, current_user
from Flasklearning.flaskyy.app.decorators import admin_required
from Flasklearning.flaskyy.app.models import Permission
from Flasklearning.flaskyy.app.decorators import permission_required, admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    page = request.args.get('page', 1, type=int)  # 渲染的页数从请求的查询字符串( request.args )中获取
    if form.validate_on_submit() and current_user.can(models.Permission.WRITE_ARTICLES):
        # 注意,新文章对象的 author 属性值为表达式 current_user._get_current_object() 。变量
        # current_user 由 Flask-Login 提供,和所有上下文变量一样,也是通过线程内的代理对象实
        # 现。这个对象的表现类似用户对象,但实际上却是一个轻度包装,包含真正的用户对象。
        # 数据库需要真正的用户对象,因此要调用 _get_current_object() 方法。
        posts = models.Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(posts)
        db.session.commit()
        return redirect(url_for('main.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = models.Post.query
    pagination = query.order_by(models.Post.timestamp.desc()).paginate(page, per_page=current_app.config[
        "FLASKY_POSTS_PER_PAGE"], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, form=form, show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(models.Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=["GET", "POST"])  # 用户级别的资料编辑器
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(message='Your profile has been updated')
        return redirect(url_for('main.user', username=current_user.username))
    # 当 form.validate_on_submit()返回 False 时,表单中的 3 个字段都使用 current_user 中保存的初始值
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])  # 管理员的资料编辑路由
@login_required
@admin_required
def edit_profile_admin(id):
    user = models.User.query.get_or_404(id)  # Like get() but aborts with 404 if not found instead of returning None.
    form = EditProfileAdminForm(user=user)  # 传入 user
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = models.Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>',methods=['GET',"POST"])  # 支持博客文章评论
def post(id):
    post = models.Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = models.Comment(body=form.body.data, post=post,
                                 author=current_user._get_current_object())  # 真正的 User 对象要使用表达式 current_user._get_current_object() 获取
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('main.post', id=post.id, pagr=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / 15 + 1
    pagination = post.comments.order_by(models.Comment.timestamp.asc()).paginate(
        page, per_page=15, error_out=False
    )
    comments=pagination.items
    return render_template('post.html', posts=[post],form=form,comments=comments,pagination=pagination)  # post.html 模板接收一个列表作为参数,必须要传入列表


@main.route('/follow/<username>')  # “关注”路由和视图函数
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash("You are already following this user.")
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    flash("You are now following %s" % username)
    return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        current_user.unfollow(user)
        flash('You have unfollowed %s' % username)
        return redirect(url_for('main.user', username=username))
    else:
        flash('You are not following this user.')
        return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')  # Ta 关注de ren路由和视图函数
def followers(username):
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page=page, per_page=15, error_out=False
    )
    follows = [
        {'user': item.follower, 'timestamp': item.timestamp}
        for item in pagination.items
    ]
    return render_template('followers.html', user=user, title='Followers of', endpoint='.followers',
                           pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')  # 关注Ta de ren路由和视图函数
def followed_by(username):
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=15, error_out=False
    )
    follows = [
        {'user': item.followed, 'timestamp': item.timestamp}
        for item in pagination.items
    ]
    return render_template('followers.html', user=user, title='Followed_by', endpoint='.followed_by',
                           pagination=pagination, follows=follows)


@main.route('/all')
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page=request.args.get('page',1,type=int)
    pagination=models.Comment.query.order_by(models.Comment.timestamp.desc()).paginate(
        page=page,per_page=15,error_out=False
    )
    comments=pagination.items
    return render_template('moderate.html',pagination=pagination,comments=comments,page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
     comment=models.Comment.query.get_or_404(id)
     comment.disable=False
     db.session.add(comment)
     db.session.commit()
     return redirect(url_for('main.moderate',page=request.args.get('page',1,type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment=models.Comment.query.get_or_404(id)
    comment.disable=True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.moderate',page=request.args.get('page',1,type=int)))

