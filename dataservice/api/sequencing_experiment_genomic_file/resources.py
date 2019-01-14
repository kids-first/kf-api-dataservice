from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.sequencing_experiment.models import (
    SequencingExperimentGenomicFile
)
from dataservice.api.sequencing_experiment_genomic_file.schemas import (
    SequencingExperimentGenomicFileSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class SequencingExperimentGenomicFileListAPI(CRUDView):
    """
    SequencingExperimentGenomicFile List API
    """
    endpoint = 'sequencing_experiment_genomic_files_list'
    rule = '/sequencing-experiment-genomic-files'
    schemas = {'SequencingExperimentGenomicFile':
               SequencingExperimentGenomicFileSchema}

    @paginated
    @use_args(filter_schema_factory(SequencingExperimentGenomicFileSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get a paginated sequencing_experiment_genomic_files
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              SequencingExperimentGenomicFile
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        q = SequencingExperimentGenomicFile.query.filter_by(**filter_params)

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.genomic_file.models import GenomicFile
        from dataservice.api.biospecimen_genomic_file.models import (
            BiospecimenGenomicFile
        )
        if study_id:
            q = (q.join(SequencingExperimentGenomicFile.genomic_file)
                 .join(GenomicFile.biospecimen_genomic_files)
                 .join(BiospecimenGenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id)
                 .group_by(SequencingExperimentGenomicFile.kf_id))

        return (SequencingExperimentGenomicFileSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new sequencing_experiment_genomic_file
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              SequencingExperimentGenomicFile
        """
        body = request.get_json(force=True)
        try:
            app = (SequencingExperimentGenomicFileSchema(strict=True)
                   .load(body).data)
        except ValidationError as err:
            abort(400,
                  'could not create sequencing_experiment_genomic_file: {}'
                  .format(err.messages))

        db.session.add(app)
        db.session.commit()
        return SequencingExperimentGenomicFileSchema(
            201,
            'sequencing_experiment_genomic_file {} created'.format(app.kf_id)
        ).jsonify(app), 201


class SequencingExperimentGenomicFileAPI(CRUDView):
    """
    SequencingExperimentGenomicFile API
    """
    endpoint = 'sequencing_experiment_genomic_files'
    rule = '/sequencing-experiment-genomic-files/<string:kf_id>'
    schemas = {'SequencingExperimentGenomicFile':
               SequencingExperimentGenomicFileSchema}

    def get(self, kf_id):
        """
        Get a sequencing_experiment_genomic_file by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              SequencingExperimentGenomicFile
        """
        app = SequencingExperimentGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_experiment_genomic_file', kf_id))

        return SequencingExperimentGenomicFileSchema().jsonify(app)

    def patch(self, kf_id):
        """
        Update an existing sequencing_experiment_genomic_file.
        Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              SequencingExperimentGenomicFile
        """
        app = SequencingExperimentGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_experiment_genomic_file', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            app = (SequencingExperimentGenomicFileSchema(strict=True)
                   .load(body, instance=app, partial=True).data)
        except ValidationError as err:
            abort(400,
                  'could not update sequencing_experiment_genomic_file: {}'
                  .format(err.messages))

        db.session.add(app)
        db.session.commit()

        return SequencingExperimentGenomicFileSchema(
            200,
            'sequencing_experiment_genomic_file {} updated'.format(app.kf_id)
        ).jsonify(app), 200

    def delete(self, kf_id):
        """
        Delete sequencing_experiment_genomic_file by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              SequencingExperimentGenomicFile
        """
        app = SequencingExperimentGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_experiment_genomic_file', kf_id))

        db.session.delete(app)
        db.session.commit()

        return SequencingExperimentGenomicFileSchema(
            200,
            'sequencing_experiment_genomic_file {} deleted'.format(app.kf_id)
        ).jsonify(app), 200
