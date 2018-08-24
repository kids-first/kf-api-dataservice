from marshmallow_sqlalchemy import field_for

from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.diagnosis.schemas import DiagnosisSchema
from dataservice.api.common.validation import validate_age
from dataservice.api.common.custom_fields import (DateOrDatetime,
                                                  PatchedURLFor)
from dataservice.api.common.validation import (validate_positive_number,
                                               enum_validation_generator,
                                               validate_kf_id)
from dataservice.extensions import ma
from marshmallow import (
    fields,
    validates
)

ANALYTE_TYPE_ENUM = {"DNA", "RNA", "Other"}


class BiospecimenSchema(BaseSchema):
    participant_id = field_for(Biospecimen, 'participant_id', required=True,
                               load_only=True)

    sequencing_center_id = field_for(Biospecimen, 'sequencing_center_id',
                                     required=True, load_only=True)

    age_at_event_days = field_for(Biospecimen, 'age_at_event_days',
                                  validate=validate_age)
    concentration_mg_per_ml = field_for(Biospecimen, 'concentration_mg_per_ml',
                                        validate=validate_positive_number)
    volume_ul = field_for(Biospecimen, 'volume_ul',
                          validate=validate_positive_number)

    shipment_date = field_for(Biospecimen, 'shipment_date',
                              field_class=DateOrDatetime)
    analyte_type = field_for(Biospecimen, 'analyte_type',
                             validate=enum_validation_generator(
                                 ANALYTE_TYPE_ENUM))
    diagnoses = fields.Nested(DiagnosisSchema, many=True, only=['kf_id'],
                              load_only=True)

    class Meta(BaseSchema.Meta):
        model = Biospecimen
        resource_url = 'api.biospecimens'
        collection_url = 'api.biospecimens_list'
        exclude = (BaseSchema.Meta.exclude +
                   ('participant', 'sequencing_center') +
                   ('genomic_files', 'biospecimen_genomic_files'))

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>'),
        'sequencing_center': ma.URLFor('api.sequencing_centers',
                                       kf_id='<sequencing_center_id>'),
        'diagnoses': PatchedURLFor('api.diagnoses_list',
                                   biospecimen_id='<kf_id>'
                                   ),
        'biospecimen_genomic_files': ma.URLFor(
            'api.biospecimen_genomic_files_list', biospecimen_id='<kf_id>')
    })


class BiospecimenFilterSchema(BiospecimenSchema):

    diagnosis_id = fields.Str()

    @validates('diagnosis_id')
    def valid_diagnosis_id(self, value):
        validate_kf_id('DG', value)
