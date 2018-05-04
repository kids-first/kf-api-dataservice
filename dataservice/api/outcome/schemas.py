from marshmallow_sqlalchemy import field_for

from dataservice.api.outcome.models import (
    Outcome, VitalStatusEnum, DiseaseRelatedEnum)
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_age
from dataservice.extensions import ma
from dataservice.api.common.custom_fields import EnumField


class OutcomeSchema(BaseSchema):

    participant_id = field_for(Outcome, 'participant_id', required=True,
                               load_only=True, example='PT_DZB048J5')
    age_at_event_days = field_for(Outcome, 'age_at_event_days',
                                  validate=validate_age, example=232)
    vital_status = EnumField(enum=[s.value for s in VitalStatusEnum])
    disease_related = EnumField(enum=[s.value for s in DiseaseRelatedEnum])

    class Meta(BaseSchema.Meta):
        model = Outcome
        resource_url = 'api.outcomes'
        collection_url = 'api.outcomes_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
