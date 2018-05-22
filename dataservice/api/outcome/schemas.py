from marshmallow_sqlalchemy import field_for

from dataservice.api.outcome.models import Outcome
from dataservice.api.common.schemas import BaseSchema, COMMON_ENUM
from dataservice.api.common.validation import (validate_age,
                                               enum_validation_generator)
from dataservice.extensions import ma
from marshmallow import post_dump

VITAL_STATUS_ENUM = {'alive': 'Alive', 'dead': 'Dead'}
DISEASE_RELATED_ENUM = {'yes': 'Yes', 'no': 'No'}
VITAL_STATUS_ENUM.update(COMMON_ENUM)
DISEASE_RELATED_ENUM.update(COMMON_ENUM)


class OutcomeSchema(BaseSchema):

    participant_id = field_for(Outcome, 'participant_id', required=True,
                               load_only=True, example='PT_DZB048J5')
    age_at_event_days = field_for(Outcome, 'age_at_event_days',
                                  validate=validate_age, example=232)
    vital_status = field_for(Outcome, 'vital_status',
                             validate=enum_validation_generator(
                                 VITAL_STATUS_ENUM))

    disease_related = field_for(Outcome, 'disease_related',
                                validate=enum_validation_generator(
                                    DISEASE_RELATED_ENUM))

    @post_dump()
    def auto_populate_enum(self, data):
        if data['vital_status'] is not None:
            data['vital_status'] = VITAL_STATUS_ENUM[
                data['vital_status'].lower()]
        if data['disease_related'] is not None:
            data['disease_related'] = DISEASE_RELATED_ENUM[
                data['disease_related'].lower()]

    class Meta(BaseSchema.Meta):
        model = Outcome
        resource_url = 'api.outcomes'
        collection_url = 'api.outcomes_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
