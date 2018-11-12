from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.cavatica_task.models import CavaticaTask
from dataservice.api.cavatica_task.schemas import (
    CavaticaTaskSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class CavaticaTaskListAPI(CRUDView):
    """
    CavaticaTask List API
    """
    endpoint = 'cavatica_tasks_list'
    rule = '/cavatica-tasks'
    schemas = {'CavaticaTask': CavaticaTaskSchema}

    @paginated
    @use_args(filter_schema_factory(CavaticaTaskSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get a paginated cavatica_tasks
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              CavaticaTask
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        q = (CavaticaTask.query
             .filter_by(**filter_params))

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.genomic_file.models import GenomicFile
        from dataservice.api.cavatica_task.models import (
            CavaticaTaskGenomicFile
        )
        from dataservice.api.biospecimen_genomic_file.models import (
            BiospecimenGenomicFile
        )

        if study_id:
            q = (q.join(CavaticaTask.cavatica_task_genomic_files)
                 .join(CavaticaTaskGenomicFile.genomic_file)
                 .join(GenomicFile.biospecimen_genomic_files)
                 .join(BiospecimenGenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id)
                 .group_by(CavaticaTask.kf_id))

        return (CavaticaTaskSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new cavatica_task
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              CavaticaTask
        """
        body = request.get_json(force=True)
        try:
            app = CavaticaTaskSchema(strict=True).load(body).data
        except ValidationError as err:
            abort(400,
                  'could not create cavatica_task: {}'.format(err.messages))

        db.session.add(app)
        db.session.commit()
        return CavaticaTaskSchema(
            201, 'cavatica_task {} created'.format(app.kf_id)
        ).jsonify(app), 201


class CavaticaTaskAPI(CRUDView):
    """
    CavaticaTask API
    """
    endpoint = 'cavatica_tasks'
    rule = '/cavatica-tasks/<string:kf_id>'
    schemas = {'CavaticaTask': CavaticaTaskSchema}

    def get(self, kf_id):
        """
        Get a cavatica_task by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              CavaticaTask
        """
        app = CavaticaTask.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_task', kf_id))

        return CavaticaTaskSchema().jsonify(app)

    def patch(self, kf_id):
        """
        Update an existing cavatica_task. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              CavaticaTask
        """
        app = CavaticaTask.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_task', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            app = CavaticaTaskSchema(strict=True).load(body, instance=app,
                                                       partial=True).data
        except ValidationError as err:
            abort(400,
                  'could not update cavatica_task: {}'.format(err.messages))

        db.session.add(app)
        db.session.commit()

        return CavaticaTaskSchema(
            200, 'cavatica_task {} updated'.format(app.kf_id)
        ).jsonify(app), 200

    def delete(self, kf_id):
        """
        Delete cavatica_task by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              CavaticaTask
        """
        app = CavaticaTask.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('cavatica_task', kf_id))

        db.session.delete(app)
        db.session.commit()

        return CavaticaTaskSchema(
            200, 'cavatica_task {} deleted'.format(app.kf_id)
        ).jsonify(app), 200
