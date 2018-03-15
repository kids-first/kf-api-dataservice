from marshmallow_sqlalchemy import field_for

from dataservice.api.sample.models import Sample
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_age
from dataservice.extensions import ma


class SampleSchema(BaseSchema):
    participant_id = field_for(Sample, 'participant_id', required=True,
                               load_only=True)
    age_at_event_days = field_for(Sample, 'age_at_event_days',
                                  validate=validate_age)

    class Meta(BaseSchema.Meta):
        model = Sample
        resource_url = 'api.samples'
        collection_url = 'api.samples_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
