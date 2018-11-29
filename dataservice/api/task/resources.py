from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.task.models import Task
from dataservice.api.task.schemas import (
    TaskSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class TaskListAPI(CRUDView):
    """
    Task List API
    """
    endpoint = 'tasks_list'
    rule = '/tasks'
    schemas = {'Task': TaskSchema}

    @paginated
    @use_args(filter_schema_factory(TaskSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get a paginated tasks
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              Task
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        q = (Task.query
             .filter_by(**filter_params))

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.genomic_file.models import GenomicFile
        from dataservice.api.task.models import (
            TaskGenomicFile
        )
        from dataservice.api.biospecimen_genomic_file.models import (
            BiospecimenGenomicFile
        )

        if study_id:
            q = (q.join(Task.task_genomic_files)
                 .join(TaskGenomicFile.genomic_file)
                 .join(GenomicFile.biospecimen_genomic_files)
                 .join(BiospecimenGenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id)
                 .group_by(Task.kf_id))

        return (TaskSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new task
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Task
        """
        body = request.get_json(force=True)
        try:
            app = TaskSchema(strict=True).load(body).data
        except ValidationError as err:
            abort(400,
                  'could not create task: {}'.format(err.messages))

        db.session.add(app)
        db.session.commit()
        return TaskSchema(
            201, 'task {} created'.format(app.kf_id)
        ).jsonify(app), 201


class TaskAPI(CRUDView):
    """
    Task API
    """
    endpoint = 'tasks'
    rule = '/tasks/<string:kf_id>'
    schemas = {'Task': TaskSchema}

    def get(self, kf_id):
        """
        Get a task by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Task
        """
        app = Task.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('task', kf_id))

        return TaskSchema().jsonify(app)

    def patch(self, kf_id):
        """
        Update an existing task. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Task
        """
        app = Task.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('task', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            app = TaskSchema(strict=True).load(body, instance=app,
                                               partial=True).data
        except ValidationError as err:
            abort(400,
                  'could not update task: {}'.format(err.messages))

        db.session.add(app)
        db.session.commit()

        return TaskSchema(
            200, 'task {} updated'.format(app.kf_id)
        ).jsonify(app), 200

    def delete(self, kf_id):
        """
        Delete task by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Task
        """
        app = Task.query.get(kf_id)
        if app is None:
            abort(404, 'could not find {} `{}`'
                  .format('task', kf_id))

        db.session.delete(app)
        db.session.commit()

        return TaskSchema(
            200, 'task {} deleted'.format(app.kf_id)
        ).jsonify(app), 200
