from marshmallow_sqlalchemy import field_for

from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.common.schemas import BaseSchema, IndexdFileSchema
from dataservice.extensions import ma


class GenomicFileSchema(BaseSchema, IndexdFileSchema):
    class Meta(BaseSchema.Meta, IndexdFileSchema.Meta):
        model = GenomicFile
        resource_url = 'api.genomic_files'
        collection_url = 'api.genomic_files_list'

    sequencing_experiment_id = field_for(GenomicFile,
                                         'sequencing_experiment_id',
                                         required=True,
                                         load_only=True)

    latest_did = field_for(GenomicFile,
                           'latest_did',
                           required=False,
                           load_only=True)

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url)
    }, description='Resource links and pagination')
