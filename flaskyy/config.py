import os


class Config:
    '''
    在 3 个子类中, SQLALCHEMY_DATABASE_URI 变量都被指定了不同的值。这样程序就可在不同
    的配置环境中运行,每个环境都使用不同的数据库。
    '''
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN="13533801264@163.com"

    @staticmethod
    def init_app(app):
        '''在这个方法中,可以执行对当前
环境的配置初始化'''
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_SUPPRESS_SEND = False
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1111@localhost/DEV'


class TestingConfig(Config):
    TESING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1111@localhost/TEST'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1111@localhost/DATA'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
