from marshmallow_sqlalchemy import field_for

from dataservice.api.cavatica_task.models import CavaticaTaskGenomicFile
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class CavaticaTaskGenomicFileSchema(BaseSchema):

    cavatica_task_id = field_for(CavaticaTaskGenomicFile, 'cavatica_task_id',
                                 required=True, load_only=True,
                                 example='CT_ABB2C104')
    genomic_file_id = field_for(CavaticaTaskGenomicFile, 'genomic_file_id',
                                required=True, load_only=True,
                                example='GF_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = CavaticaTaskGenomicFile
        resource_url = 'api.cavatica_task_genomic_files'
        collection_url = 'api.cavatica_task_genomic_files_list'
        exclude = BaseSchema.Meta.exclude + ('cavatica_task', 'genomic_file')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'cavatica_task': ma.URLFor('api.cavatica_tasks',
                                   kf_id='<cavatica_task_id>'),
        'genomic_file': ma.URLFor('api.genomic_files',
                                  kf_id='<genomic_file_id>')
    })
