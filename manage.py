#!/usr/bin/env python
import os

from dataservice import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """ Run the unit tests and pep8 checks """
    from subprocess import call
    call(["python","-m","pytest","tests"])
    call(["python","-m","pytest","--pep8","dataservice"])


@manager.command
def deploy():
    """ Run deployment tasks """
    from flask.ext.migrate import upgrade

    # migrate database to latest revision
    upgrade()


if __name__ == '__main__':
    manager.run()
