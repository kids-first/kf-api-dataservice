from marshmallow_sqlalchemy import field_for
from dataservice.api.participant.models import Participant

from dataservice.api.common.schemas import BaseSchema, COMMON_ENUM
from dataservice.extensions import ma
from marshmallow import post_dump
from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.api.common.validation import enum_validation_generator

# Enum Choices for participant fields

GENDER_ENUM = {'male': 'Male', 'female': 'Female', 'other': 'Other'}
ETHNICITY_ENUM = {'hispanic or latino': 'Hispanic or Latino',
                  'not hispanic or latino': 'Not Hispanic or Latino'}
RACE_ENUM = {
    'white': 'White',
    'american indian or alaska native':
    'American Indian or Alaska Native',
    'black or african american':
    'Black or African American',
    'asian': 'Asian',
    'native hawaiian or other pacific islander':
    'Native Hawaiian or Other Pacific Islander',
    'other': 'Other'}
GENDER_ENUM.update(COMMON_ENUM)
ETHNICITY_ENUM.update(COMMON_ENUM)
RACE_ENUM.update(COMMON_ENUM)


class ParticipantSchema(BaseSchema):
    study_id = field_for(Participant, 'study_id', required=True,
                         load_only=True)
    family_id = field_for(Participant, 'family_id',
                          load_only=True,
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

    @post_dump()
    def auto_populate_enum(self, data):
        if data['gender'] is not None:
            data['gender'] = GENDER_ENUM[data['gender'].lower()]
        if data['ethnicity'].lower() is not None:
            data['ethnicity'] = ETHNICITY_ENUM[data['ethnicity'].
                                               lower()]
        if data['race'] is not None:
            data['race'] = RACE_ENUM[data['race'].lower()]

    class Meta(BaseSchema.Meta):
        model = Participant
        resource_url = 'api.participants'
        collection_url = 'api.participants_list'
        exclude = (BaseSchema.Meta.exclude +
                   ('study', 'family') +
                   ('diagnoses', 'phenotypes', 'outcomes', 'biospecimens'))

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'study': ma.URLFor('api.studies', kf_id='<study_id>'),
        'family': PatchedURLFor('api.families', kf_id='<family_id>'),
        'diagnoses': ma.URLFor('api.diagnoses_list', participant_id='<kf_id>'),
        'phenotypes': ma.URLFor('api.phenotypes_list',
                                participant_id='<kf_id>'),
        'outcomes': ma.URLFor('api.outcomes_list',
                              participant_id='<kf_id>'),
        'biospecimens': ma.URLFor('api.biospecimens_list',
                                  participant_id='<kf_id>'),
        'family_relationships': ma.URLFor('api.family_relationships_list',
                                          participant_id='<kf_id>')
    })
