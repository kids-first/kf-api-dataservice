from dataservice.api.investigator.models import Investigator
from dataservice.api.common.schemas import BaseSchema, FilterSchemaMixin
from dataservice.extensions import ma


class InvestigatorSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Investigator
        resource_url = 'api.investigators'
        collection_url = 'api.investigators_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url)
    })


class InvestigatorFilterSchema(FilterSchemaMixin, InvestigatorSchema):
    pass
