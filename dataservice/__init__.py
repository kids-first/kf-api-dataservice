# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask

from dataservice import commands
from dataservice.extensions import db, ma, migrate
from dataservice.api.participant.models import Participant
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
    register_error_handlers(app)
    register_blueprints(app)

    return app


def register_shellcontext(app):
    """
    Register shell context objects
    """

    def shell_context():
        """Shell context objects."""
        return {'db': db,
                'Participant': Participant}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """
    Register Click commands
    """
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.erd)


def register_extensions(app):
    """
    Register Flask extensions
    """

    # SQLAlchemy
    db.init_app(app)
    ma.init_app(app)

    # If using sqlite, must instruct sqlalchemy to set foreign key constraint
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        from sqlalchemy.engine import Engine
        from sqlalchemy import event

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # Migrate
    migrate.init_app(app, db)


def register_error_handlers(app):
    """
    Register error handlers
    """
    from dataservice.api import errors
    from werkzeug.exceptions import HTTPException
    app.register_error_handler(HTTPException, errors.http_error)
    app.register_error_handler(404, errors.http_error)
    app.register_error_handler(400, errors.http_error)


def register_blueprints(app):
    from dataservice.api import api
    app.register_blueprint(api)
