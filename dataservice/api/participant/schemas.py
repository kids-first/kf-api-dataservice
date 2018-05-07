from marshmallow_sqlalchemy import field_for
from dataservice.api.participant.models import Participant

from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma

from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.api.common.validation import enum_validation_generator

# Enum Choices for participant fields

GENDER_ENUM = {'Male', 'Female'}
ETHNICITY_ENUM = {'Hispanic or Latino',
                  'Not Hispanic or Latino'}
RACE_ENUM = {
    'White', 'American Indian or Alaska Native',
    'Black or African American', 'Asian',
    'Native Hawaiian or Other Pacific Islander',
    'Other'}


class ParticipantSchema(BaseSchema):
    study_id = field_for(Participant, 'study_id', required=True,
                         load_only=True)
    family_id = field_for(Participant, 'family_id',
                          required=False, example='FM_ABB2C104')
    gender = field_for(Participant, 'gender',
                       validate=enum_validation_generator(
                           GENDER_ENUM))
    ethnicity = field_for(Participant, 'ethnicity',
                          validate=enum_validation_generator(
                              ETHNICITY_ENUM))
    race = field_for(Participant, 'race',
                     validate=enum_validation_generator(
                         RACE_ENUM))

    class Meta(BaseSchema.Meta):
        model = Participant
        resource_url = 'api.participants'
        collection_url = 'api.participants_list'
        exclude = BaseSchema.Meta.exclude + ('study', 'family')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'study': ma.URLFor('api.studies', kf_id='<study_id>'),
        'family': PatchedURLFor('api.families', kf_id='<family_id>')
    })
