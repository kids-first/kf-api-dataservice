from marshmallow_sqlalchemy import field_for

from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.common.schemas import BaseSchema, COMMON_ENUM
from dataservice.api.common.validation import (validate_age,
                                               enum_validation_generator)
from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.extensions import ma
from marshmallow import post_dump

DIAGNOSIS_CATEGORY_ENUM = {'structural birth defect':
                           'Structural Birth Defect',
                           'cancer': 'Cancer',
                           'other': 'Other'}
DIAGNOSIS_CATEGORY_ENUM.update(COMMON_ENUM)


class DiagnosisSchema(BaseSchema):
    participant_id = field_for(Diagnosis, 'participant_id', required=True,
                               load_only=True, example='PT_DZB048J5')
    biospecimen_id = field_for(Diagnosis, 'biospecimen_id', required=False,
                               load_only=True, example='BS_DZB048J5')
    age_at_event_days = field_for(Diagnosis, 'age_at_event_days',
                                  validate=validate_age, example=232)
    diagnosis_category = field_for(Diagnosis, 'diagnosis_category',
                                   validate=enum_validation_generator(
                                       DIAGNOSIS_CATEGORY_ENUM))

    @post_dump()
    def auto_populate_enum(self, data):
        if data['diagnosis_category'] is not None:
            data['diagnosis_category'] = DIAGNOSIS_CATEGORY_ENUM[data[
                'diagnosis_category'].lower()]

    class Meta(BaseSchema.Meta):
        model = Diagnosis
        resource_url = 'api.diagnoses'
        collection_url = 'api.diagnoses_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>'),
        'biospecimen': PatchedURLFor('api.biospecimens',
                                     kf_id='<biospecimen_id>')
    })
