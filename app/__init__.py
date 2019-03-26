from flask import Flask
from werkzeug.utils import find_modules, import_string

from config import config
from .extensions import db, mail, jwt


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    app.config.from_pyfile('config.py', silent=True)

    # celery.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    # socket.init_app(app) 需要eventlet服务器
    # cache.init_app(app)  需要redis
    # configure_uploads(app, attachments) config里需要配置

    register_blueprints(app, 'v1', 'app.apis.v1')
    return app


def register_blueprints(app, v, package):
    for module_name in find_modules(package):
        module = import_string(module_name)
        if hasattr(module, 'bp'):
            bp = module.bp
            app.register_blueprint(bp, url_prefix='/api/{0}/{1}'.format(v, bp.name))