# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask

from dataservice import commands
from dataservice.extensions import db, migrate
from dataservice.api.person.models import Person
from config import config


def create_app(config_name):
    """
    An application factory
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config[config_name])

    # Register Flask extensions
    register_extensions(app)
    register_shellcontext(app)
    register_commands(app)
    register_blueprints(app)

    return app


def register_shellcontext(app):
    """
    Register shell context objects
    """

    def shell_context():
        """Shell context objects."""
        return {'db': db,
                'Person': Person}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """
    Register Click commands
    """
    app.cli.add_command(commands.test)


def register_extensions(app):
    """
    Register Flask extensions
    """

    # SQLAlchemy
    db.init_app(app)

    # Migrate
    migrate.init_app(app, db)


def register_error_handlers(app):
    """
    Register error handlers
    """
    pass


def register_blueprints(app):
    from dataservice.api import api_v1
    app.register_blueprint(api_v1)
