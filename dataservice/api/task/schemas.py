from marshmallow_sqlalchemy import field_for

from dataservice.api.cavatica_task.models import CavaticaTask
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.extensions import ma


class CavaticaTaskSchema(BaseSchema):

    cavatica_app_id = field_for(CavaticaTask, 'cavatica_app_id',
                                load_only=True, required=False,
                                example='CA_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = CavaticaTask
        resource_url = 'api.cavatica_tasks'
        collection_url = 'api.cavatica_tasks_list'
        exclude = (BaseSchema.Meta.exclude + ('cavatica_app', ) +
                   ('cavatica_task_genomic_files',))

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'cavatica_app': PatchedURLFor('api.cavatica_apps',
                                      kf_id='<cavatica_app_id>'),
        'cavatica_task_genomic_files': ma.URLFor(
            'api.cavatica_task_genomic_files_list', cavatica_task_id='<kf_id>')
    })
