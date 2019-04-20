import os
from app import create_app, db, mail, jwt, models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# worker = celery
manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def hello():
    return 'Hello,zhj'


@manager.shell
def make_shell_context():
    context = dict(app=app, db=db, mail=mail, jwt=jwt)
    context.update(vars(models))
    return context


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
