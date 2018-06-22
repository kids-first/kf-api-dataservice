from marshmallow_sqlalchemy import field_for
from marshmallow import (
    fields,
    validates
)

from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_kf_id
from dataservice.extensions import ma


class FamilyRelationshipSchema(BaseSchema):
    participant1_id = field_for(FamilyRelationship, 'participant1_id',
                                required=True,
                                load_only=True, example='PT_B048J5')
    participant2_id = field_for(FamilyRelationship, 'participant2_id',
                                required=True,
                                load_only=True, example='PT_B048J6')

    class Meta(BaseSchema.Meta):
        model = FamilyRelationship
        resource_url = 'api.family_relationships'
        collection_url = 'api.family_relationships_list'
        exclude = BaseSchema.Meta.exclude + ('participant2', 'participant1')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant1': ma.URLFor('api.participants',
                                  kf_id='<participant1_id>'),
        'participant2': ma.URLFor('api.participants',
                                  kf_id='<participant2_id>')
    })


class FamilyRelationshipFilterSchema(FamilyRelationshipSchema):

    participant_id = fields.Str()

    @validates('study_id')
    def valid(self, value):
        validate_kf_id('PT', value)
