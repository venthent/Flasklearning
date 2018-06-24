from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from Flasklearning.flaskyy.app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', flags=0,
                                                          message="Usernames must have only letters,numbers, dots or underscores")])
    password = PasswordField("PassWord", validators=[DataRequired(), Length(4, 32),
                                                     EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField("Please confirm your password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        '''如 果 表 单 类 中 定 义 了 以
validate_ 开头且后面跟着字段名的方法,这个方法就和常规的验证函数一起调用'''
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")


class ChangePasswordForm(FlaskForm):
    old_password=PasswordField('Old password:',validators=[DataRequired()])
    password=PasswordField('New password',validators=[DataRequired(),EqualTo('password2',message='Passwords must match')])
    password2=PasswordField('Confirm your password again',validators=[DataRequired()])
    submit=SubmitField("Upgrade password")