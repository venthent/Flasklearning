from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, Email, Regexp
from flask_pagedown.fields import PageDownField
from Flasklearning.flaskyy.app.models import Role, User


class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EditProfileForm(FlaskForm):
    name = StringField("Real Name:", validators=[DataRequired(), Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")


class EditProfileAdminForm(FlaskForm):  # 管理员使用的资料编辑表单
    name = StringField("Real Name:", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About me")

    email = StringField('Email', validators=[DataRequired(), Email(), Length(0, 64)])
    username = StringField('Username', validators=[DataRequired(), Length(0, 64),
                                                   Regexp('^[A-Za-z][A-Aa-z0-9._]*$', flags=0,
                                                          message='Usernames must have only letters, numbers, dots'
                                                                  'or underscores')])
    confirmed = BooleanField("Confirmed")
    role = SelectField('Role', coerce=int)  # coerce=int 参数,从而把字段的值转换为整数
    submit = SubmitField("Submit")

    def __init__(self, user, *args, **kwargs):  # Here is difficult to understand
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        '''如 果 表 单 类 中 定 义 了 以
        validate_ 开头且后面跟着字段名的方法,这个方法就和常规的验证函数一起调用,just is 自定义的验证方法.
mail 和 username 字段的构造方式和认证表单中的一样,但处理验证时需要更加小心。验
证这两个字段时,首先要检查字段的值是否发生了变化,如果有变化,就要保证新值不
和其他用户的相应字段值重复;如果字段值没有变化,则应该跳过验证。为了实现这个逻辑,表单构造函数接收用户对象作为参数,并将其保存在成员变量中,随后自定义的验证
方法要使用这个用户对象'''
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered ")

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use")

#博客文章表单
class PostForm(FlaskForm):
    body=PageDownField("What's on your mind?",validators=[DataRequired()]) #启用 Markdown 的文章表单
    #body=TextAreaField("Say something:",validators=[DataRequired()])
    submit=SubmitField('Submit')

#评论输入表单
class CommentForm(FlaskForm):
    body=StringField('',validators=[DataRequired()])
    submit=SubmitField('Comment')

