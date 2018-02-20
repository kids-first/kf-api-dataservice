from marshmallow_sqlalchemy import field_for

from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class GenomicFileSchema(BaseSchema):
    __endpoint__ = 'api.genomic_files'
    class Meta(BaseSchema.Meta):
        model = GenomicFile
        resource_url = 'api.genomic_files'
        collection_url = 'api.genomic_files_list'

    sequencing_experiment_id = field_for(GenomicFile,
                                         'sequencing_experiment_id',
                                         required=False,
                                         load_only=True)

    urls = ma.List(ma.Str())
    file_name = ma.Str()
    rev = ma.Str()
    hashes = ma.Dict()
    metadata = ma.Dict(attribute='_metadata')
    size = ma.Int()

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>')
    }, description='Resource links and pagination')
