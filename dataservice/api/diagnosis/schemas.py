from marshmallow_sqlalchemy import field_for

from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import (validate_age,
                                               validate_ontology_id_prefix,
                                               FieldValidator,
                                               enum_validation_generator)
from dataservice.api.common.custom_fields import PatchedURLFor

from dataservice.extensions import ma


DIAGNOSIS_CATEGORY_ENUM = {'Structural Birth Defect',
                           'Cancer',
                           'Other'}


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
    mondo_id_diagnosis = FieldValidator(attribute='mondo_id_diagnosis',
                                        validate=validate_ontology_id_prefix)
    icd_id_diagnosis = FieldValidator(attribute='icd_id_diagnosis',
                                      validate=validate_ontology_id_prefix)
    uberon_id_tumor_location = FieldValidator(
        attribute='uberon_id_tumor_location',
        validate=validate_ontology_id_prefix)
    ncit_id_diagnosis = FieldValidator(attribute='ncit_id_diagnosis',
                                       validate=validate_ontology_id_prefix)

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
