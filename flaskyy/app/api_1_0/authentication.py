from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify
from Flasklearning.flaskyy.app.models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbiden

auth = HTTPBasicAuth()


@auth.verify_password
def varify_password(email_or_token, password):
    '''电子邮件和密码使用 User 模型中现有的方法验证。如果登录密令正确,这个验证回调函数
就返回 True ,否则返回 False'''
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None

    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verity_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbiden(message='Unconfirmed account')


@api.route('/token')  # 生成认证令牌
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token':g.current_user.generate_auth_token(expiration=3600),'expiration':3600})

