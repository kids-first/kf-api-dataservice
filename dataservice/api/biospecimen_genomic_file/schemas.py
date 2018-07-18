from marshmallow_sqlalchemy import field_for

from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile)
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class BiospecimenGenomicFileSchema(BaseSchema):

    biospecimen_id = field_for(BiospecimenGenomicFile, 'biospecimen_id',
                               required=True, load_only=True,
                               example='BS_ABC2C104')
    genomic_file_id = field_for(BiospecimenGenomicFile, 'genomic_file_id',
                                required=True, load_only=True,
                                example='GF_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = BiospecimenGenomicFile
        resource_url = 'api.biospecimen_genomic_files'
        collection_url = 'api.biospecimen_genomic_files_list'
        exclude = BaseSchema.Meta.exclude + ('biospecimen', 'genomic_file')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'biospecimen': ma.URLFor('api.biospecimens',
                                 kf_id='<biospecimen_id>'),
        'genomic_file': ma.URLFor('api.genomic_files',
                                  kf_id='<genomic_file_id>')
    })
