from marshmallow_sqlalchemy import field_for
from marshmallow import (
    fields,
    validates
)

from dataservice.extensions import ma
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_age
from dataservice.api.common.custom_fields import DateOrDatetime
from dataservice.api.common.validation import (
    validate_positive_number,
    enum_validation_generator,
    validate_kf_id,
    list_validation_generator
)

ANALYTE_TYPE_ENUM = {"DNA", "RNA", "Other", "Virtual"}
SAMPLE_PROCUREMENT_ENUM = {"Autopsy", "Biopsy", "Subtotal Resections",
                           "Gross Total Resections", "Blood Draw",
                           "Bone Marrow Aspiration", "Other"}
# Codes from http://purl.obolibrary.org/obo/duo.owl
DUO_ID_BIOSPECIMEN_ENUM = {
    "DUO:0000021", "DUO:0000006", "DUO:0000019", "DUO:0000026", "DUO:0000020",
    "DUO:0000005", "DUO:0000018", "DUO:0000012", "DUO:0000025", "DUO:0000004",
    "DUO:0000011", "DUO:0000024", "DUO:0000016", "DUO:0000029", "DUO:0000028",
    "DUO:0000022", "DUO:0000007", "DUO:0000042", "DUO:0000014", "DUO:0000027"
}


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
    method_of_sample_procurement = field_for(
        Biospecimen,
        'method_of_sample_procurement',
        validate=enum_validation_generator(SAMPLE_PROCUREMENT_ENUM)
    )
    duo_ids = field_for(
        Biospecimen,
        'duo_ids',
        validate=list_validation_generator(DUO_ID_BIOSPECIMEN_ENUM,
                                           items_name='DUO IDs')
    )

    class Meta(BaseSchema.Meta):
        model = Biospecimen
        resource_url = 'api.biospecimens'
        collection_url = 'api.biospecimens_list'
        exclude = (BaseSchema.Meta.exclude +
                   ('participant', 'sequencing_center') +
                   ('biospecimen_genomic_files', 'biospecimen_diagnoses'))

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>'),
        'sequencing_center': ma.URLFor('api.sequencing_centers',
                                       kf_id='<sequencing_center_id>'),
        'biospecimen_genomic_files': ma.URLFor(
            'api.biospecimen_genomic_files_list', biospecimen_id='<kf_id>'),
        'biospecimen_diagnoses': ma.URLFor(
            'api.biospecimen_diagnoses_list', biospecimen_id='<kf_id>'),
        'diagnoses': ma.URLFor('api.diagnoses_list',
                               biospecimen_id='<kf_id>'),
        'genomic_files': ma.URLFor('api.genomic_files_list',
                                   biospecimen_id='<kf_id>')
    })


class BiospecimenFilterSchema(BiospecimenSchema):

    diagnosis_id = fields.Str()
    genomic_file_id = fields.Str()

    @validates('diagnosis_id')
    def valid_diagnosis_id(self, value):
        validate_kf_id('DG', value)

    @validates('genomic_file_id')
    def valid_genomic_file_id(self, value):
        validate_kf_id('GF', value)
