from marshmallow_sqlalchemy import field_for
from marshmallow import (
    fields,
    validates
)

from dataservice.extensions import ma
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import (
    validate_age,
    enum_validation_generator,
    validate_kf_id
)


DIAGNOSIS_CATEGORY_ENUM = {'Structural Birth Defect',
                           'Cancer',
                           'Other'}


class DiagnosisSchema(BaseSchema):
    participant_id = field_for(Diagnosis, 'participant_id', required=True,
                               load_only=True, example='PT_DZB048J5')
    age_at_event_days = field_for(Diagnosis, 'age_at_event_days',
                                  validate=validate_age, example=232)
    diagnosis_category = field_for(Diagnosis, 'diagnosis_category',
                                   validate=enum_validation_generator(
                                       DIAGNOSIS_CATEGORY_ENUM))

    class Meta(BaseSchema.Meta):
        model = Diagnosis
        resource_url = 'api.diagnoses'
        collection_url = 'api.diagnoses_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>'),
        'biospecimen_diagnoses': ma.URLFor('api.biospecimen_diagnoses_list',
                                           diagnosis_id='<kf_id>'),
        'biospecimens': ma.URLFor('api.biospecimens_list',
                                  diagnosis_id='<kf_id>')
    })


class DiagnosisFilterSchema(DiagnosisSchema):

    biospecimen_id = fields.Str()

    @validates('biospecimen_id')
    def valid_biospecimen_id(self, value):
        validate_kf_id('BS', value)
