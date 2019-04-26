import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    SECRET_KEY = 'hard to guess string'
    # MAIL SETTING
    # MAIL_SERVER = 'smtp.test.com'
    # MAIL_PORT = 587
    # MAIL_USE_SSL = False
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = '1264728987@qq.com'
    MAIL_PASSWORD = 'fiahqxsroytmbaag'
    # JWT SETTING
    # JWT_SECRET_KEY = 'hard to guess'
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'ShineMory'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)
    # RESTFUL SETTING
    ERROR_404_HELP = False
    # SQLALCHEMY SETTING
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True


class DevelopmentConfig(Config):
    # DEBUG = True
    # SQLALCHEMY SETTING
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    #     os.path.join(base_dir, 'dev.sqlite')
    # SQLALCHEMY_DATABASE_URI = \
    #     'mysql+pymysql://root:hzmcdba@localhost/test?charset=utf8'
    # SQLALCHEMY_DATABASE_URI = \
    #     'mysql+pymysql://root:hzmcdba@172.16.200.215/test?charset=utf8'
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://root:admin@127.0.0.1/shinemory?charset=utf8'
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 120
    SQLALCHEMY_POOL_TIMEOUT = 20


class TestingConfig(Config):
    TESTING = True
    SERVER_NAME = 'okp'
    # SQLALCHEMY SETTING
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'develop': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}