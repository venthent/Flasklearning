from Flasklearning.flaskyy.app import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from Flasklearning.flaskyy.app import login_manager

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role % r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        # 如果试图读取 password 属性的值,则会返回错误
        raise AttributeError('password is not a readable attribute')

    @password.setter  # .setter is that Write Only
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verity_password(self, password):
        '''verify_password 方 法 接 受 一 个 参 数( 即 密 码 )
, 将 其 传 给 Werkzeug 提 供 的 check_
password_hash() 函数,和存储在 User 模型中的密码散列值进行比对。如果这个方法返回
True ,就表明密码是正确的'''
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User % r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    '''回调函数接收以 Unicode 字符串形式表示的用户标识符'''
    return User.query.get(int(user_id))