from flask import render_template, url_for, flash, redirect, request, g
from Flasklearning.flaskyy.app.auth import auth
from flask_login import logout_user, login_user, login_required, current_user
from Flasklearning.flaskyy.app.models import User
from .forms import LoginForm, RegistrationForm
from Flasklearning.flaskyy.app import db
from Flasklearning.flaskyy.app.email import send_async_email, send_email
from flask_login import current_user


@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verity_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(message='Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logout')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = User(email=register_form.email.data,
                    username=register_form.username.data,
                    password=register_form.password.data)
        db.session.add(user)
        db.session.commit()#提交数据库之后才能赋予新用户 id 值,而确认令
#牌需要用到 id ,所以不能延后提交。
        token = user.generate_confirmation_token()
        send_email(subject='Confirm your account', to=[register_form.email.data], template="auth/mail/confirm",
                   user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=register_form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """The function is to confirm user by sending email"""
    if current_user.confirmed is True:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_app_request():
    '''同时满足以下 3 个条件时, before_app_request 处理程序会拦截请求。
(1) 用户已登录( current_user.is_authenticated() 必须返回 True )。
(2) 用户的账户还未确认。
(3) 请求的端点(使用 request.endpoint 获取)不在认证蓝本中。访问认证路由要获取权
限,因为这些路由的作用是让用户确认账户或执行其他账户管理操作。 There is hard to '''
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5]!="auth." and request.endpoint!='static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(subject='Confirm your account again!', to=[current_user.email], template="auth/mail/confirm",
                   user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))