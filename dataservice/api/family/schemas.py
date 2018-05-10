from dataservice.api.family.models import Family
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class FamilySchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = Family
        resource_url = 'api.families'
        collection_url = 'api.families_list'
        exclude = BaseSchema.Meta.exclude + ('participants', )

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participants': ma.URLFor('api.participants_list', family_id='<kf_id>')
    })
