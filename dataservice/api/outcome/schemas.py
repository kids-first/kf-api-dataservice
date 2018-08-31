from marshmallow_sqlalchemy import field_for

from dataservice.api.outcome.models import Outcome
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import (validate_age,
                                               enum_validation_generator)
from dataservice.extensions import ma


VITAL_STATUS_ENUM = {'Alive', 'Deceased'}
DISEASE_RELATED_ENUM = {'Yes', 'No'}


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

    class Meta(BaseSchema.Meta):
        model = Outcome
        resource_url = 'api.outcomes'
        collection_url = 'api.outcomes_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
