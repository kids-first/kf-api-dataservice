from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.sequencing_experiment.models import (
    SequencingExperiment,
    SequencingExperimentGenomicFile
)
from dataservice.api.sequencing_experiment.schemas import (
    SequencingExperimentSchema,
    SequencingExperimentFilterSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class SequencingExperimentListAPI(CRUDView):
    """
    SequencingExperiment REST API
    """
    endpoint = 'sequencing_experiments_list'
    rule = '/sequencing-experiments'
    schemas = {'SequencingExperiment': SequencingExperimentSchema}

    @paginated
    @use_args(filter_schema_factory(SequencingExperimentFilterSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get all sequencing_experiments
        ---
        description: Get all sequencing_experiments
        template:
          path:
            get_list.yml
          properties:
            resource:
              SequencingExperiment
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        # Get genomic file id and remove from model filter params
        genomic_file_id = filter_params.pop('genomic_file_id', None)

        q = (SequencingExperiment.query
             .filter_by(**filter_params))

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.genomic_file.models import GenomicFile
        from dataservice.api.biospecimen_genomic_file.models import (
            BiospecimenGenomicFile
        )

        if study_id:
            q = (q.join(SequencingExperiment
                        .sequencing_experiment_genomic_files)
                 .join(SequencingExperimentGenomicFile.genomic_file)
                 .join(GenomicFile.biospecimen_genomic_files)
                 .join(BiospecimenGenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id)
                 .group_by(SequencingExperiment.kf_id))

        # Filter by genomic_file_id
        if genomic_file_id:
            q = (q.join(
                SequencingExperimentGenomicFile,
                SequencingExperiment.kf_id ==
                SequencingExperimentGenomicFile.sequencing_experiment_id)
                .filter(SequencingExperimentGenomicFile.genomic_file_id ==
                        genomic_file_id))

        return (SequencingExperimentSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new sequencing_experiment
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              SequencingExperiment
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            se = SequencingExperimentSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create sequencing_experiment: {}'
                  .format(e.messages))

        # Add to and save in database
        db.session.add(se)
        db.session.commit()

        return SequencingExperimentSchema(201,
                                          'sequencing_experiment {} created'
                                          .format(se.kf_id)).jsonify(se), 201


class SequencingExperimentAPI(CRUDView):
    """
    SequencingExperiment REST API
    """
    endpoint = 'sequencing_experiments'
    rule = '/sequencing-experiments/<string:kf_id>'
    schemas = {'SequencingExperiment': SequencingExperimentSchema}

    def get(self, kf_id):
        """
        Get a sequencing_experiment by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              SequencingExperiment
        """
        # Get one
        se = SequencingExperiment.query.get(kf_id)
        if se is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_experiment', kf_id))
        return SequencingExperimentSchema().jsonify(se)

    def patch(self, kf_id):
        """
        Update an existing sequencing_experiment.

        Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              SequencingExperiment
        """
        se = SequencingExperiment.query.get(kf_id)
        if se is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_experiment', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            se = (SequencingExperimentSchema(strict=True).
                  load(body, instance=se,
                       partial=True).data)
        except ValidationError as err:
            abort(400, 'could not update sequencing_experiment: {}'
                  .format(err.messages))

        db.session.add(se)
        db.session.commit()

        return SequencingExperimentSchema(
            200, 'sequencing_experiment {} updated'.format(se.kf_id)
        ).jsonify(se), 200

    def delete(self, kf_id):
        """
        Delete sequencing_experiment by id

        Deletes a sequencing_experiment given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              SequencingExperiment
        """

        # Check if sequencing_experiment exists
        se = SequencingExperiment.query.get(kf_id)
        if se is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_experiment', kf_id))

        # Save in database
        db.session.delete(se)
        db.session.commit()

        return SequencingExperimentSchema(200,
                                          'sequencing_experiment {} deleted'
                                          .format(se.kf_id)).jsonify(se), 200
