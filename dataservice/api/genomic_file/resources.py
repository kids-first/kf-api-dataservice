import datetime
from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, indexd_pagination
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.genomic_file.schemas import (
    GenomicFileSchema,
    GenomicFileFilterSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class GenomicFileListAPI(CRUDView):
    """
    GenomicFile API
    """
    endpoint = 'genomic_files_list'
    rule = '/genomic-files'
    schemas = {'GenomicFile': GenomicFileSchema}

    @paginated
    @use_args(filter_schema_factory(GenomicFileFilterSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get paginated genomic_files

        Retrieves the genomic files stored in the datamodel, then fetch
        additional properties that are stored in indexd under the same uuid.
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              GenomicFile
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        # Get read group id and remove from model filter params
        sequencing_experiment_id = filter_params.pop(
            'sequencing_experiment_id', None)

        # Get read group id and remove from model filter params
        read_group_id = filter_params.pop('read_group_id', None)

        # Get biospecimen id and remove from model filter params
        biospecimen_id = filter_params.pop('biospecimen_id', None)

        # Apply model filter params
        q = (GenomicFile.query
             .filter_by(**filter_params))

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.biospecimen_genomic_file.models import (
            BiospecimenGenomicFile
        )
        if study_id:
            q = (q.join(GenomicFile.biospecimen_genomic_files)
                 .join(BiospecimenGenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id)
                 .group_by(GenomicFile.kf_id))

        from dataservice.api.read_group.models import ReadGroupGenomicFile
        from dataservice.api.sequencing_experiment.models import (
            SequencingExperimentGenomicFile
        )

        if sequencing_experiment_id:
            q = (q.join(SequencingExperimentGenomicFile)
                 .filter(
                 SequencingExperimentGenomicFile.sequencing_experiment_id ==
                 sequencing_experiment_id)
                 )
        if read_group_id:
            q = (q.join(ReadGroupGenomicFile)
                 .filter(ReadGroupGenomicFile.read_group_id == read_group_id))
        if biospecimen_id and not study_id:
            q = (q.join(BiospecimenGenomicFile).filter(
                 BiospecimenGenomicFile.biospecimen_id == biospecimen_id))
        # This check is to remove duplicate join on biospecimen genomic file
        if biospecimen_id and study_id:
            q = (q.filter(
                 BiospecimenGenomicFile.biospecimen_id == biospecimen_id))
        pager = indexd_pagination(q, after, limit)

        return (GenomicFileSchema(many=True)
                .jsonify(pager))

    def post(self):
        """
        Create a new genomic_file
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              GenomicFile
        """
        body = request.get_json(force=True)
        try:
            gf = GenomicFileSchema(strict=True).load(body).data
        except ValidationError as err:
            abort(400,
                  'could not create genomic_file: {}'.format(err.messages))

        db.session.add(gf)
        db.session.commit()

        return GenomicFileSchema(
            201, 'genomic_file {} created'.format(gf.kf_id)
        ).jsonify(gf), 201


class GenomicFileAPI(CRUDView):
    """
    GenomicFile API
    """
    endpoint = 'genomic_files'
    rule = '/genomic-files/<string:kf_id>'
    schemas = {'GenomicFile': GenomicFileSchema}

    def get(self, kf_id):
        """
        Get a genomic file by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              GenomicFile
        """
        genomic_file = GenomicFile.query.get(kf_id)
        if genomic_file is None:
            abort(404, 'could not find {} `{}`'
                  .format('genomic_file', kf_id))

        sch = GenomicFileSchema(many=False)
        return sch.jsonify(genomic_file)

    def patch(self, kf_id):
        """
        Update an existing genomic_file
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              GenomicFile
        """
        body = request.get_json(force=True) or {}
        gf = GenomicFile.query.get(kf_id)
        if gf is None:
            abort(404, 'could not find {} `{}`'
                  .format('genomic_file', kf_id))

        # Deserialization will require this field and won't merge automatically
        if 'sequencing_experiment_id' not in body:
            body['sequencing_experiment_id'] = gf.sequencing_experiment_id

        try:
            gf = GenomicFileSchema(strict=True).load(body, instance=gf,
                                                     partial=True).data
        except ValidationError as err:
            abort(400,
                  'could not update genomic_file: {}'.format(err.messages))

        # The object won't be updated if only indexd fields are updated.
        # Explicitly update the one of the mapped fields to force an update
        # to the database.
        gf.modified_at = datetime.datetime.now()

        db.session.add(gf)
        db.session.commit()

        return GenomicFileSchema(
            200, 'genomic_file {} updated'.format(gf.kf_id)
        ).jsonify(gf), 200

    def delete(self, kf_id):
        """
        Delete genomic_file by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              GenomicFile
        """
        gf = GenomicFile.query.get(kf_id)
        if gf is None:
            abort(404, 'could not find {} `{}`'.format('genomic_file', kf_id))

        db.session.delete(gf)
        db.session.commit()

        return GenomicFileSchema(
            200, 'genomic_file {} deleted'.format(gf.kf_id)
        ).jsonify(gf), 200
