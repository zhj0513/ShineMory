import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    SECRET_KEY = 'hard to guess string'
    # JWT SETTING
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'ShineMory'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)
    # RESTFUL SETTING
    ERROR_404_HELP = False
    # SQLALCHEMY SETTING
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False


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
    # SQLALCHEMY_POOL_SIZE = 100
    # SQLALCHEMY_POOL_RECYCLE = 120
    # SQLALCHEMY_POOL_TIMEOUT = 20


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