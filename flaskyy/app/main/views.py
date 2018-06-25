from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash
from Flasklearning.flaskyy.app.main import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from Flasklearning.flaskyy.app import db, models
from flask_login import login_required, current_user
from Flasklearning.flaskyy.app.decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.name.data).first()
        old_name = session.get('name')
        if user is None:
            user = models.User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        # 蓝本中可以省略蓝本名,例如 url_for('.
        # index') 。在这种写法中,命名空间是当前请求所在的蓝本
        return redirect(url_for('.index'))
    return render_template('index.html', name=session.get('name'), form=form, known=session.get('known', False))


@main.route('/user/<username>')
def user(username):
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    else:
        return render_template('user.html', user=user)


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
        return redirect(url_for('main.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data =user.confirmed
    form.name.data =user.name
    form.location.data =user.location
    form.about_me.data =user.about_me
    return render_template('edit_profile.html',form=form,user=user)