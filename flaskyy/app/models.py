from datetime import datetime
import bleach
from flask import current_app
from markdown import markdown
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from Flasklearning.flaskyy.app import db
from Flasklearning.flaskyy.app import login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)  # index如果设为True，创建索引，提升查询效率
    permissions = db.Column(db.Integer)
    user = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        '''将角色手动添加到数据库中既耗时又容易出错。作为替代,我们要在 Role 类中添加一个类
方法,完成这个操作'''
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (
                Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,
                False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role % r>' % self.name


class Follow(db.Model):  # 关注关联表的模型实现
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())  # db.String 和 db.Text 的区别在于后者不需要指定最大长度。
    # 注意, datetime.utcnow 后面没有 () ,因为 db.Column()
    # 的 default 参数可以接受函数作为默认值
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',  # lazy 参数都在“一”这一侧设定
        cascade='all,delete-orphan'
    )
    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all,delete-orphan'
    )
    comments=db.relationship('Comment',backref='author',lazy='dynamic')#users与 comments 表之间的一对多关系

    def __init__(self, **kwargs):
        '''用户在程序中注册账户时,会被赋予适当的角色。大多数用户在注册时赋予的角色都是
    “用户”,因为这是默认角色。唯一的例外是管理员,管理员在最开始就应该赋予“管理
    员”角色。管理员由保存在设置变量 FLASKY_ADMIN 中的电子邮件地址识别,只要这个电子
    邮件地址出现在注册请求中,就会被赋予正确的角色.User 类的构造函数首先调用基类的构造函数,如果创建基类对象后还没定义角色,则根据
    电子邮件地址决定将其设为管理员还是默认角色'''
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def generate_confirmation_token(self, expiration=3600):
        # 确认用户账户
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        # db.session.add(self)
        return True

    def can(self, permissions):
        '''User 模型中添加的 can() 方法在请求和赋予角色这两种权限之间进行位与操作。如果角色
    中包含请求的所有权限位,则返回 True ,表示允许用户执行此项操作'''
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def follow(self, user):
        if not self.is_following(user=user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter_by(followed_id = user.id).first() is not None


    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def password(self):
        # 如果试图读取 password 属性的值,则会返回错误
        raise AttributeError('password is not a readable attribute')

    @password.setter  # .setter is that Write Only
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def generate_fake(count=100):
        '''生成虚拟用户和博客文章'''
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                email=forgery_py.internet.email_address(),
                username=forgery_py.internet.user_name(),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
                name=forgery_py.name.full_name(),
                location=forgery_py.address.city(),
                about_me=forgery_py.lorem_ipsum.sentence(),
                member_since=forgery_py.date.date(True)
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    @property
    def followed_posts(self):#获取所关注用户的文章
        return Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)

    def verity_password(self, password):
        '''verify_password 方 法 接 受 一 个 参 数( 即 密 码 )
    , 将 其 传 给 Werkzeug 提 供 的 check_
    password_hash() 函数,和存储在 User 模型中的密码散列值进行比对。如果这个方法返回
    True ,就表明密码是正确的'''
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()

    def __repr__(self):
        return '<User % r>' % self.username


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # utcnow need not "()"
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    comments=db.relationship('Comment',backref='post',lazy='dynamic') #posts 表与 comments 表之间的一对多关系

    @staticmethod
    def on_changed_body(target, value, oldervalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html', tags=allowed_tags, strip=True)))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            # 我们使用 offset() 查询过滤器。
            # 这个过滤器会跳过参数中指定的记录数量。通过设定一个随机的偏移值,再调用 first()
            # 方法,就能每次都获得一个不同的随机用户
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(
                body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                timestamp=forgery_py.date.date(True),
                author=u
            )
            db.session.add(p)
            db.session.commit()

class Comment(db.Model): #Comment 模型
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    body_html=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disable=db.Column(db.Boolean)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags=[
            'a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
            'strong'
        ]
        target.body_html=bleach.linkify(
            bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True)
        )


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    @property
    def confirmed(self):
        return False

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == None)

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    '''回调函数接收以 Unicode 字符串形式表示的用户标识符'''
    return User.query.get(int(user_id))


db.event.listen(Post.body, 'set', Post.on_changed_body)  # on_changed_body 函数注册在 body 字段上,是 SQLAlchemy“set”事件的监听程序
db.event.listen(Comment.body,'set',Comment.on_changed_body)