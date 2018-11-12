from marshmallow_sqlalchemy import field_for

from dataservice.api.task.models import Task
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.extensions import ma


class TaskSchema(BaseSchema):

    cavatica_app_id = field_for(Task, 'cavatica_app_id',
                                load_only=True, required=False,
                                example='CA_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = Task
        resource_url = 'api.tasks'
        collection_url = 'api.tasks_list'
        exclude = (BaseSchema.Meta.exclude + ('app', ) +
                   ('task_genomic_files',))

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'cavatica_app': PatchedURLFor('api.cavatica_apps',
                                      kf_id='<cavatica_app_id>'),
        'task_genomic_files': ma.URLFor(
            'api.task_genomic_files_list', task_id='<kf_id>')
    })
