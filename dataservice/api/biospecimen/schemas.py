from marshmallow_sqlalchemy import field_for

from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_age
from dataservice.api.common.custom_fields import DateOrDatetime
from dataservice.api.common.validation import validate_positive_number
from dataservice.extensions import ma


class BiospecimenSchema(BaseSchema):
    participant_id = field_for(Biospecimen, 'participant_id', required=True,
                               load_only=True)
    age_at_event_days = field_for(Biospecimen, 'age_at_event_days',
                                  validate=validate_age)
    concentration_mg_per_ml = field_for(Biospecimen, 'concentration_mg_per_ml',
                                        validate=validate_positive_number)
    volume_ml = field_for(Biospecimen, 'volume_ml',
                          validate=validate_positive_number)

    shipment_date = DateOrDatetime(allow_none=True)

    sequencing_center_id = field_for(Biospecimen, 'sequencing_center_id',
                                     required=True, load_only=True)

    class Meta(BaseSchema.Meta):
        model = Biospecimen
        resource_url = 'api.biospecimens'
        collection_url = 'api.biospecimens_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>'),
        'sequencing_center': ma.URLFor('api.sequencing_centers',
                                       kf_id='<sequencing_center_id>')
    })
