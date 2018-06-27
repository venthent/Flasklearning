from datetime import datetime
from flask import Flask, render_template, redirect, session, url_for, flash
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from Flasklearning.flaskyy import config
from flask_login import LoginManager
from flask_mail import Message,Mail
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
mail=Mail()
pagedown=PageDown()
#session_protection 属性可以设为 None 、 'basic' 或 'strong' ,以提
#供不同的安全等级防止用户会话遭篡改。设为 'strong' 时,Flask-Login 会记录客户端 IP
#地址和浏览器的用户代理信息,如果发现异动就登出用户
login_manager.session_protection='strong'
login_manager.login_view = 'auth.login'  # login_view 属性设置登录页面的端点,Flask-Login 需要知道哪个视图允许用户登录,
                                         # 登录路由在蓝本中定义,因此要在前面加上蓝本的名字


def create_app(config_name):
    from .main import main as main_bluprint
    from .auth import auth as auth_bluprint
    app = Flask(__name__)
    app.config.from_object(config.config[config_name])
    config.config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)

    app.register_blueprint(main_bluprint)
    # url_prefix 是可选参数。如果使用了这个参数,注册后蓝本中定义的
    # 所有路由都会加上指定的前缀,即这个例子中的 /auth。例如,/login 路由会注册成 /auth/
    # login
    app.register_blueprint(auth_bluprint, url_prefix='/auth')
    return app
