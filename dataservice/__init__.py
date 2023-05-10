# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import re
import requests
import subprocess
from flask import Flask
from alembic.config import Config
from alembic import command

from dataservice import commands
from dataservice.utils import _get_version
from dataservice.extensions import db, ma, indexd, migrate
from dataservice.api.investigator.models import Investigator
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.family.models import Family
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.read_group.models import (
    ReadGroup,
    ReadGroupGenomicFile
)
from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile
)
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.task.models import (
    Task,
    TaskGenomicFile
)
from dataservice.api.cavatica_app.models import CavaticaApp
from dataservice.api.study_file.models import StudyFile
from config import config

from sqlalchemy.exc import IntegrityError


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
    prefetch_status(app)

    if not (app.config['TESTING']):
        import logging
        import requests
        requests.packages.urllib3.add_stderr_logger()

    return app


def register_spec(app):
    """
    Creates an API spec and puts it on the app
    """
    from apispec import APISpec
    from apispec_webframeworks.flask import FlaskPlugin
    from apispec.ext.marshmallow import MarshmallowPlugin

    spec = APISpec(
        title='Kids First Data Service',
        version=_get_version(),
        openapi_version="2.0",
        plugins=[
            FlaskPlugin(),
            MarshmallowPlugin()
        ],
    )

    from dataservice.api import status_view, views
    from dataservice.api.common.schemas import StatusSchema

    spec.components.schema('Status', schema=StatusSchema)

    from dataservice.api.common.views import CRUDView
    CRUDView.register_spec(spec)
    with app.test_request_context():
        spec.path(view=status_view)
        for view in views:
            spec.path(view=view)

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
    indexd.init_app(app)

    # Migrate
    migrate.init_app(app, db)


def register_error_handlers(app):
    """
    Register error handlers

    NB: Exceptions to be handled must be imported in the head of this module
    """
    from dataservice.api import errors
    # Database integrity error
    app.register_error_handler(IntegrityError, errors.integrity_error)

    # Database validation errors
    app.register_error_handler(errors.DatabaseValidationError,
                               errors.database_validation_error)
    # Http errors
    from werkzeug.exceptions import default_exceptions
    for ex in default_exceptions:
        app.register_error_handler(ex, errors.http_error)


def register_blueprints(app):
    from dataservice.api import api
    app.register_blueprint(api)


def prefetch_status(app):
    """
    Pre-computes the status response by making system calls to get git branch
    info and python package version

    This saves the api from having to make a system level call during a request
    """
    app.config['GIT_COMMIT'] = (subprocess.check_output(
                                ['git', 'rev-parse', '--short', 'HEAD'])
                                .decode("utf-8").strip())

    app.config['GIT_BRANCH'] = (subprocess.check_output(
                                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
                                .decode("utf-8").strip())

    tags = (subprocess.check_output(
            ['git', 'tag', '-l', '--points-at', 'HEAD'])
            .decode('utf-8').split('\n'))

    app.config['GIT_TAGS'] = [] if tags[0] == '' else tags
    app.config['PKG_VERSION'] = _get_version()
