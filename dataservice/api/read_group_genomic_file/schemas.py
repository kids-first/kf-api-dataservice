from marshmallow_sqlalchemy import field_for

from dataservice.api.read_group.models import ReadGroupGenomicFile
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class ReadGroupGenomicFileSchema(BaseSchema):

    read_group_id = field_for(ReadGroupGenomicFile, 'read_group_id',
                              required=True, load_only=True,
                              example='RF_ABB2C104')
    genomic_file_id = field_for(ReadGroupGenomicFile, 'genomic_file_id',
                                required=True, load_only=True,
                                example='GF_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = ReadGroupGenomicFile
        resource_url = 'api.read_group_genomic_files'
        collection_url = 'api.read_group_genomic_files_list'
        exclude = BaseSchema.Meta.exclude + ('read_group', 'genomic_file')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'read_group': ma.URLFor('api.read_groups',
                                kf_id='<read_group_id>'),
        'genomic_file': ma.URLFor('api.genomic_files',
                                  kf_id='<genomic_file_id>')
    })
