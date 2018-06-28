from marshmallow_sqlalchemy import field_for

from dataservice.api.common.schemas import BaseSchema, COMMON_ENUM
from dataservice.api.read_group.models import ReadGroup
from dataservice.api.common.validation import (validate_positive_number,
                                               enum_validation_generator)
from dataservice.extensions import ma

PAIRED_END_ENUM = {'1': 1, '2': 2}
QUALITY_SCALE_ENUM = {'Illumina13': 'Illumina13', 'Illumina15': 'Illumina15',
                      'Illumina18': 'Illumina18',
                      'Solexa': 'Solexa', 'Sanger': 'Sanger'}
QUALITY_SCALE_ENUM.update(COMMON_ENUM)


class ReadGroupSchema(BaseSchema):

    paired_end = field_for(ReadGroup, 'paired_end',
                           validate=enum_validation_generator(
                               PAIRED_END_ENUM))

    lane_number = field_for(ReadGroup, 'lane_number',
                            validate=validate_positive_number)

    quality_scale = field_for(ReadGroup, 'quality_scale',
                              validate=enum_validation_generator(
                                  QUALITY_SCALE_ENUM))

    genomic_file_id = field_for(ReadGroup, 'genomic_file_id',
                                required=True, load_only=True)

    class Meta(BaseSchema.Meta):
        resource_url = 'api.read_groups'
        collection_url = 'api.read_groups_list'
        model = ReadGroup
        exclude = (BaseSchema.Meta.exclude +
                   ('genomic_file', ))

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'genomic_file': ma.URLFor('api.genomic_files',
                                  kf_id='<genomic_file_id>')
    }, description='Resource links and pagination')
