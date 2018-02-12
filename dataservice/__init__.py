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
    register_admin(app)

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


def register_admin(app):
    import flask_admin as admin
    from flask_admin.contrib import sqla
    from flask.ext.admin.model.form import InlineFormAdmin
    from flask.ext.admin.contrib.sqla import ModelView
    from flask.ext.admin.contrib.sqla.form import InlineModelConverter
    from flask.ext.admin.contrib.sqla.fields import InlineModelFormList

    from dataservice.api.participant.models import Participant
    from dataservice.api.demographic.models import Demographic
    from dataservice.api.diagnosis.models import Diagnosis
    from dataservice.api.sample.models import Sample
    from dataservice.api.genomic_file.models import GenomicFile
    from dataservice.api.sequencing_experiment.models import (
        SequencingExperiment
    )
    from dataservice.api.aliquot.models import Aliquot

    class IndexView(admin.AdminIndexView):
        @admin.expose('/')
        def index(self):
            counts = {}
            entities = [Participant,
                        Demographic,
                        Diagnosis,
                        Sample,
                        GenomicFile,
                        SequencingExperiment,
                        Aliquot]

            for e in entities:
                counts[e.__name__] = e.query.count()

            quality = {}

            # Demographic metric
            with_dem = Participant.query.join(Demographic).count()
            tot = Participant.query.count()
            msg = '{} / {}'.format(with_dem, tot)
            quality['participants_with_demographic'] = msg

            with_samp = (Participant.query
                         .filter(Participant.samples.any())
                         .count())
            tot = Participant.query.count()
            msg = '{} / {}'.format(with_samp, tot)
            quality['participants_with_at_least_one_sample'] = msg

            with_experiment = (Aliquot.query
                               .filter(Aliquot.sequencing_experiments.any())
                               .count())
            tot = Aliquot.query.count()
            msg = '{} / {}'.format(with_experiment, tot)
            quality['aliquots_with_at_least_one_sequencing_experiment'] = msg

            with_file = (SequencingExperiment.query
                         .filter(SequencingExperiment.genomic_files.any())
                         .count())
            tot = SequencingExperiment.query.count()
            msg = '{} / {}'.format(with_file, tot)
            quality['sequencing_experiments_with_at_least_one_file'] = msg

            return self.render('admin/index.html',
                               counts=counts,
                               quality=quality)

    class GenomicFileAdmin(sqla.ModelView):
        column_display_pk = True
        column_exclude_list = ['uuid', 'md5sum', 'sequencing_experiments']
        column_searchable_list = ('kf_id',)
        column_sortable_list = ('created_at', 'modified_at')

    class InlineDemographic(InlineFormAdmin):
        def __init__(self):
            super(InlineDemographic, self).__init__(Diagnosis)

    class ParticipantAdmin(sqla.ModelView):
        column_display_pk = True
        column_exclude_list = ['uuid', ]
        column_searchable_list = ('external_id', 'kf_id')
        column_sortable_list = ('created_at', 'modified_at')
        # column_auto_select_related = True
        inline_models = (InlineDemographic(),)

    admin = admin.Admin(app, name='Dataservice',
                        index_view=IndexView(),
                        template_mode='bootstrap3')
    admin.add_view(ParticipantAdmin(Participant, db.session))
    admin.add_view(GenomicFileAdmin(GenomicFile, db.session))
