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
from flask_mail import Message, Mail
from Flasklearning.flaskyy import config

bootstrap = Bootstrap()
mail=Mail()
moment=Moment()
db=SQLAlchemy()


def create_app(config_name):
    from .main import main as main_bluprint
    app=Flask(__name__)
    app.config.from_object(config.config[config_name])
    config.config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    app.register_blueprint(main_bluprint)
    return app

