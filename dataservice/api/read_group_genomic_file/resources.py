from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.read_group.models import (
    ReadGroupGenomicFile
)
from dataservice.api.read_group_genomic_file.schemas import (
    ReadGroupGenomicFileSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class ReadGroupGenomicFileListAPI(CRUDView):
    """
    ReadGroupGenomicFile List API
    """
    endpoint = 'read_group_genomic_files_list'
    rule = '/read-group-genomic-files'
    schemas = {'ReadGroupGenomicFile': ReadGroupGenomicFileSchema}

    @paginated
    @use_args(filter_schema_factory(ReadGroupGenomicFileSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get a paginated read_group_genomic_files
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              ReadGroupGenomicFile
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        q = ReadGroupGenomicFile.query.filter_by(**filter_params)

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.genomic_file.models import GenomicFile
        from dataservice.api.biospecimen_genomic_file.models import (
            BiospecimenGenomicFile
        )
        if study_id:
            q = (q.join(ReadGroupGenomicFile.genomic_file)
                 .join(GenomicFile.biospecimen_genomic_files)
                 .join(BiospecimenGenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id)
                 .group_by(ReadGroupGenomicFile.kf_id))

        return (ReadGroupGenomicFileSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new read_group_genomic_file
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              ReadGroupGenomicFile
        """
        body = request.get_json(force=True)
        try:
            app = (ReadGroupGenomicFileSchema(strict=True)
                   .load(body).data)
        except ValidationError as err:
            abort(400,
                  'could not create read_group_genomic_file: {}'
                  .format(err.messages))

        db.session.add(app)
        db.session.commit()
        return ReadGroupGenomicFileSchema(
            201, 'read_group_genomic_file {} created'.format(app.kf_id)
        ).jsonify(app), 201


class ReadGroupGenomicFileAPI(CRUDView):
    """
    ReadGroupGenomicFile API
    """
    endpoint = 'read_group_genomic_files'
    rule = '/read-group-genomic-files/<string:kf_id>'
    schemas = {'ReadGroupGenomicFile': ReadGroupGenomicFileSchema}

    def get(self, kf_id):
        """
        Get a read_group_genomic_file by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              ReadGroupGenomicFile
        """
        app = ReadGroupGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('read_group_genomic_file', kf_id))

        return ReadGroupGenomicFileSchema().jsonify(app)

    def patch(self, kf_id):
        """
        Update an existing read_group_genomic_file. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              ReadGroupGenomicFile
        """
        app = ReadGroupGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('read_group_genomic_file', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            app = (ReadGroupGenomicFileSchema(strict=True)
                   .load(body, instance=app, partial=True).data)
        except ValidationError as err:
            abort(400,
                  'could not update read_group_genomic_file: {}'
                  .format(err.messages))

        db.session.add(app)
        db.session.commit()

        return ReadGroupGenomicFileSchema(
            200, 'read_group_genomic_file {} updated'.format(app.kf_id)
        ).jsonify(app), 200

    def delete(self, kf_id):
        """
        Delete read_group_genomic_file by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              ReadGroupGenomicFile
        """
        app = ReadGroupGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('read_group_genomic_file', kf_id))

        db.session.delete(app)
        db.session.commit()

        return ReadGroupGenomicFileSchema(
            200, 'read_group_genomic_file {} deleted'.format(app.kf_id)
        ).jsonify(app), 200
