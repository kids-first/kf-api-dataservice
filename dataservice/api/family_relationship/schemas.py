from marshmallow_sqlalchemy import field_for

from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.common.schemas import BaseSchema, FilterSchemaMixin
from dataservice.extensions import ma


class FamilyRelationshipSchema(BaseSchema):
    participant_id = field_for(FamilyRelationship, 'participant_id',
                               required=True,
                               load_only=True, example='PT_B048J5')
    relative_id = field_for(FamilyRelationship, 'relative_id',
                            required=True,
                            load_only=True, example='PT_B048J6')

    class Meta(BaseSchema.Meta):
        model = FamilyRelationship
        resource_url = 'api.family_relationships'
        collection_url = 'api.family_relationships_list'
        exclude = BaseSchema.Meta.exclude + ('relative', 'participant')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>'),
        'relative': ma.URLFor('api.participants', kf_id='<relative_id>')
    })


class FamilyRelationshipFilterSchema(FilterSchemaMixin,
                                     FamilyRelationshipSchema):
    pass
