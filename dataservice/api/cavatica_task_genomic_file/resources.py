from flask import abort, request
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.cavatica_task.models import (
    CavaticaTaskGenomicFile
)
from dataservice.api.cavatica_task_genomic_file.schemas import (
    CavaticaTaskGenomicFileSchema
)
from dataservice.api.common.views import CRUDView


class CavaticaTaskGenomicFileListAPI(CRUDView):
    """
    CavaticaTaskGenomicFile List API
    """
    endpoint = 'cavatica_task_genomic_files_list'
    rule = '/cavatica-task-genomic-files'
    schemas = {'CavaticaTaskGenomicFile': CavaticaTaskGenomicFileSchema}

    @paginated
    def get(self, after, limit):
        """
        Get a paginated cavatica_task_genomic_files
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              CavaticaTaskGenomicFile
        """
        q = CavaticaTaskGenomicFile.query

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.genomic_file.models import GenomicFile

        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(CavaticaTaskGenomicFile.genomic_file)
                 .join(GenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id))

        return (CavaticaTaskGenomicFileSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new cavatica_task_genomic_file
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              CavaticaTaskGenomicFile
        """
        body = request.get_json(force=True)
        try:
            app = (CavaticaTaskGenomicFileSchema(strict=True)
                   .load(body).data)
        except ValidationError as err:
            abort(400,
                  'could not create cavatica_task_genomic_file: {}'
                  .format(err.messages))

        db.session.add(app)
        db.session.commit()
        return CavaticaTaskGenomicFileSchema(
            201, 'cavatica_task_genomic_file {} created'.format(app.kf_id)
        ).jsonify(app), 201


class CavaticaTaskGenomicFileAPI(CRUDView):
    """
    CavaticaTaskGenomicFile API
    """
    endpoint = 'cavatica_task_genomic_files'
    rule = '/cavatica-task-genomic-files/<string:kf_id>'
    schemas = {'CavaticaTaskGenomicFile': CavaticaTaskGenomicFileSchema}

    def get(self, kf_id):
        """
        Get a cavatica_task_genomic_file by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              CavaticaTaskGenomicFile
        """
        app = CavaticaTaskGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_task_genomic_file', kf_id))

        return CavaticaTaskGenomicFileSchema().jsonify(app)

    def patch(self, kf_id):
        """
        Update an existing cavatica_task_genomic_file. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              CavaticaTaskGenomicFile
        """
        app = CavaticaTaskGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_task_genomic_file', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            app = (CavaticaTaskGenomicFileSchema(strict=True)
                   .load(body, instance=app, partial=True).data)
        except ValidationError as err:
            abort(400,
                  'could not update cavatica_task_genomic_file: {}'
                  .format(err.messages))

        db.session.add(app)
        db.session.commit()

        return CavaticaTaskGenomicFileSchema(
            200, 'cavatica_task_genomic_file {} updated'.format(app.kf_id)
        ).jsonify(app), 200

    def delete(self, kf_id):
        """
        Delete cavatica_task_genomic_file by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              CavaticaTaskGenomicFile
        """
        app = CavaticaTaskGenomicFile.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_task_genomic_file', kf_id))

        db.session.delete(app)
        db.session.commit()

        return CavaticaTaskGenomicFileSchema(
            200, 'cavatica_task_genomic_file {} deleted'.format(app.kf_id)
        ).jsonify(app), 200
