from marshmallow_sqlalchemy import field_for
from marshmallow import (
    fields,
    validates
)

from dataservice.extensions import ma
from dataservice.api.sample.models import Sample
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_age
from dataservice.api.common.custom_fields import DateOrDatetime
from dataservice.api.common.validation import (
    validate_positive_number,
    enum_validation_generator,
    validate_kf_id,
    list_validation_generator
)


class SampleSchema(BaseSchema):
    participant_id = field_for(Sample, 'participant_id', required=True,
                               load_only=True)

    class Meta(BaseSchema.Meta):
        model = Sample
        resource_url = 'api.samples'
        collection_url = 'api.samples_list'
        exclude = (BaseSchema.Meta.exclude + ('participant', 'containers'))

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>'),
        'containers': ma.URLFor('api.containers_list',
                                sample_id='<kf_id>'),
    })
