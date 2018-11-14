from marshmallow_sqlalchemy import field_for

from dataservice.api.task.models import TaskGenomicFile
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class TaskGenomicFileSchema(BaseSchema):

    task_id = field_for(TaskGenomicFile, 'task_id',
                        required=True, load_only=True,
                        example='TK_ABB2C104')
    genomic_file_id = field_for(TaskGenomicFile, 'genomic_file_id',
                                required=True, load_only=True,
                                example='GF_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = TaskGenomicFile
        resource_url = 'api.task_genomic_files'
        collection_url = 'api.task_genomic_files_list'
        exclude = BaseSchema.Meta.exclude + ('task', 'genomic_file')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'task': ma.URLFor('api.tasks', kf_id='<task_id>'),
        'genomic_file': ma.URLFor('api.genomic_files',
                                  kf_id='<genomic_file_id>')
    })
