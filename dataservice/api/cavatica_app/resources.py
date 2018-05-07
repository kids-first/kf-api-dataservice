from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.cavatica_app.models import CavaticaApp
from dataservice.api.cavatica_app.schemas import CavaticaAppSchema
from dataservice.api.common.views import CRUDView


class CavaticaAppListAPI(CRUDView):
    """
    CavaticaApp List API
    """
    endpoint = 'cavatica_apps_list'
    rule = '/cavatica-apps'
    schemas = {'CavaticaApp': CavaticaAppSchema}

    @paginated
    def get(self, after, limit):
        """
        Get a paginated cavatica_apps
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              CavaticaApp
        """
        q = CavaticaApp.query.options(joinedload(CavaticaApp.cavatica_tasks)
                                      .load_only('kf_id'))

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.genomic_file.models import GenomicFile
        from dataservice.api.cavatica_task.models import (
            CavaticaTask,
            CavaticaTaskGenomicFile
        )

        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(CavaticaApp.cavatica_tasks)
                 .join(CavaticaTask.cavatica_task_genomic_files)
                 .join(CavaticaTaskGenomicFile.genomic_file)
                 .join(GenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id)
                 .group_by(CavaticaApp.kf_id))

        return (CavaticaAppSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new cavatica_app
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              CavaticaApp
        """
        body = request.get_json(force=True)
        try:
            app = CavaticaAppSchema(strict=True).load(body).data
        except ValidationError as err:
            abort(400,
                  'could not create cavatica_app: {}'.format(err.messages))

        db.session.add(app)
        db.session.commit()
        return CavaticaAppSchema(
            201, 'cavatica_app {} created'.format(app.kf_id)
        ).jsonify(app), 201


class CavaticaAppAPI(CRUDView):
    """
    CavaticaApp API
    """
    endpoint = 'cavatica_apps'
    rule = '/cavatica-apps/<string:kf_id>'
    schemas = {'CavaticaApp': CavaticaAppSchema}

    def get(self, kf_id):
        """
        Get a cavatica_app by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              CavaticaApp
        """
        app = CavaticaApp.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_app', kf_id))

        return CavaticaAppSchema().jsonify(app)

    def patch(self, kf_id):
        """
        Update an existing cavatica_app. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              CavaticaApp
        """
        app = CavaticaApp.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_app', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            app = CavaticaAppSchema(strict=True).load(body, instance=app,
                                                      partial=True).data
        except ValidationError as err:
            abort(400,
                  'could not update cavatica_app: {}'.format(err.messages))

        db.session.add(app)
        db.session.commit()

        return CavaticaAppSchema(
            200, 'cavatica_app {} updated'.format(app.kf_id)
        ).jsonify(app), 200

    def delete(self, kf_id):
        """
        Delete cavatica_app by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              CavaticaApp
        """
        app = CavaticaApp.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_app', kf_id))

        db.session.delete(app)
        db.session.commit()

        return CavaticaAppSchema(
            200, 'cavatica_app {} deleted'.format(app.kf_id)
        ).jsonify(app), 200
