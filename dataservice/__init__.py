# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask

from dataservice import commands
from dataservice.extensions import db, ma, migrate
from dataservice.api.participant.models import Participant
from config import config

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException


def create_app(config_name):
    """
    An application factory
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Register Flask extensions
    register_extensions(app)
    register_shellcontext(app)
    register_commands(app)
    register_error_handlers(app)
    register_blueprints(app)
    register_spec(app)

    return app


def register_spec(app):
    """
    Creates an API spec and puts it on the app
    """
    from apispec import APISpec

    spec = APISpec(
        title='Kids First Data Service',
        version='1.0.0',
        plugins=[
            'apispec.ext.flask',
            'apispec.ext.marshmallow',
        ],
    )

    from dataservice.api.common.schemas import StatusSchema, response_generator, paginated_generator
    from dataservice.api.participant.schemas import ParticipantSchema
    from dataservice.api.diagnosis.schemas import DiagnosisSchema
    from dataservice.api.demographic.schemas import DemographicSchema

    from dataservice.api import (
        status_view,
        participant_view,
        participant_list_view,
        diagnosis_view,
        diagnosis_list_view
    )

    spec.definition('Status', schema=StatusSchema)
    spec.definition('Participant', schema=ParticipantSchema)
    ParticipantResponseSchema = response_generator(ParticipantSchema)
    spec.definition('ParticipantResponse', schema=ParticipantResponseSchema)
    ParticipantPaginatedSchema = paginated_generator(ParticipantSchema)
    spec.definition('ParticipantPaginated', schema=ParticipantPaginatedSchema)

    spec.definition('Diagnosis', schema=DiagnosisSchema)
    DiagnosisResponseSchema = response_generator(DiagnosisSchema)
    spec.definition('DiagnosisResponse', schema=DiagnosisResponseSchema)
    DiagnosisPaginatedSchema = paginated_generator(DiagnosisSchema)
    spec.definition('DiagnosisPaginated', schema=DiagnosisPaginatedSchema)

    from flask import current_app

    with app.test_request_context():
        spec.add_path(view=status_view)
        spec.add_path(view=participant_view)
        spec.add_path(view=participant_list_view)

        spec.add_path(view=diagnosis_view)
        spec.add_path(view=diagnosis_list_view)

    app.spec = spec


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
    app.cli.add_command(commands.populate_db)
    app.cli.add_command(commands.clear_db)


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

    NB: Exceptions to be handled must be imported in the head of this module
    """
    from dataservice.api import errors
    app.register_error_handler(HTTPException, errors.http_error)
    app.register_error_handler(IntegrityError, errors.integrity_error)
    app.register_error_handler(404, errors.http_error)
    app.register_error_handler(400, errors.http_error)


def register_blueprints(app):
    from dataservice.api import api
    app.register_blueprint(api)
