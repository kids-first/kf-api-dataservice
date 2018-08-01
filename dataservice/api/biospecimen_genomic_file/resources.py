from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile
)
from dataservice.api.biospecimen_genomic_file.schemas import (
    BiospecimenGenomicFileSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class BiospecimenGenomicFileListAPI(CRUDView):
    """
    BiospecimenGenomicFile List API
    """
    endpoint = 'biospecimen_genomic_files_list'
    rule = '/biospecimen-genomic-files'
    schemas = {'BiospecimenGenomicFile': BiospecimenGenomicFileSchema}

    @paginated
    @use_args(filter_schema_factory(BiospecimenGenomicFileSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get a paginated biospecimen_genomic_files
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              BiospecimenGenomicFile
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        q = BiospecimenGenomicFile.query.filter_by(**filter_params)

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen

        if study_id:
            q = (q.join(BiospecimenGenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id))

        return (BiospecimenGenomicFileSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new biospecimen_genomic_file
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              BiospecimenGenomicFile
        """
        body = request.get_json(force=True)
        try:
            bs_gf = (BiospecimenGenomicFileSchema(strict=True)
                     .load(body).data)
        except ValidationError as err:
            abort(400,
                  'could not create biospecimen_genomic_file: {}'
                  .format(err.messages))

        db.session.add(bs_gf)
        db.session.commit()
        return BiospecimenGenomicFileSchema(
            201, 'biospecimen_genomic_file {} created'.format(bs_gf.kf_id)
        ).jsonify(bs_gf), 201


class BiospecimenGenomicFileAPI(CRUDView):
    """
    BiospecimenGenomicFile API
    """
    endpoint = 'biospecimen_genomic_files'
    rule = '/biospecimen-genomic-files/<string:kf_id>'
    schemas = {'BiospecimenGenomicFile': BiospecimenGenomicFileSchema}

    def get(self, kf_id):
        """
        Get a biospecimen_genomic_file by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              BiospecimenGenomicFile
        """
        bs_gf = BiospecimenGenomicFile.query.get(kf_id)
        if bs_gf is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen_genomic_file', kf_id))

        return BiospecimenGenomicFileSchema().jsonify(bs_gf)

    def patch(self, kf_id):
        """
        Update an existing biospecimen_genomic_file. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              BiospecimenGenomicFile
        """
        bs_gf = BiospecimenGenomicFile.query.get(kf_id)
        if bs_gf is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen_genomic_file', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            bs_gf = (BiospecimenGenomicFileSchema(strict=True)
                     .load(body, instance=bs_gf, partial=True).data)
        except ValidationError as err:
            abort(400,
                  'could not update biospecimen_genomic_file: {}'
                  .format(err.messages))

        db.session.add(bs_gf)
        db.session.commit()

        return BiospecimenGenomicFileSchema(
            200, 'biospecimen_genomic_file {} updated'.format(bs_gf.kf_id)
        ).jsonify(bs_gf), 200

    def delete(self, kf_id):
        """
        Delete biospecimen_genomic_file by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              BiospecimenGenomicFile
        """
        bs_gf = BiospecimenGenomicFile.query.get(kf_id)
        if bs_gf is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen_genomic_file', kf_id))

        db.session.delete(bs_gf)
        db.session.commit()

        return BiospecimenGenomicFileSchema(
            200, 'biospecimen_genomic_file {} deleted'.format(bs_gf.kf_id)
        ).jsonify(bs_gf), 200
