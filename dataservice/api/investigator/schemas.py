from dataservice.api.investigator.models import Investigator
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class InvestigatorSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Investigator
        resource_url = 'api.investigators'
        collection_url = 'api.investigators_list'
        exclude = BaseSchema.Meta.exclude + ('studies', )

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'studies': ma.URLFor('api.studies_list', investigator_id='<kf_id>')
    })
