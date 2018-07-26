from marshmallow_sqlalchemy import field_for

from dataservice.api.biospecimen_diagnosis.models import (
    BiospecimenDiagnosis)
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class BiospecimenDiagnosisSchema(BaseSchema):

    biospecimen_id = field_for(BiospecimenDiagnosis, 'biospecimen_id',
                               required=True, load_only=True,
                               example='BS_ABC2C104')
    diagnosis_id = field_for(BiospecimenDiagnosis, 'diagnosis_id',
                             required=True, load_only=True,
                             example='DG_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = BiospecimenDiagnosis
        resource_url = 'api.biospecimen_diagnoses'
        collection_url = 'api.biospecimen_diagnoses_list'
        exclude = BaseSchema.Meta.exclude + ('biospecimen', 'diagnosis')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'biospecimen': ma.URLFor('api.biospecimens',
                                 kf_id='<biospecimen_id>'),
        'diagnosis': ma.URLFor('api.diagnoses',
                               kf_id='<diagnosis_id>')
    })
