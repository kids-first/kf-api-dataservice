from marshmallow_sqlalchemy import field_for

from dataservice.api.aliquot.models import Aliquot
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.custom_fields import DateOrDatetime
from dataservice.api.common.validation import validate_positive_number
from dataservice.extensions import ma


class AliquotSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        resource_url = 'api.aliquots'
        collection_url = 'api.aliquots_list'
        model = Aliquot

    sample_id = field_for(Aliquot, 'sample_id', required=True, load_only=True)

    concentration = field_for(Aliquot, 'concentration',
                              validate=validate_positive_number)
    volume = field_for(Aliquot, 'volume',
                       validate=validate_positive_number)

    shipment_date = DateOrDatetime()

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'sample': ma.URLFor('api.samples', kf_id='<sample_id>'),
    }, description='Resource links and pagination')
