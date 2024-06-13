from marshmallow_sqlalchemy import field_for
from marshmallow import (
    fields,
    validates
)

from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.api.sample_relationship.models import SampleRelationship
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_kf_id
from dataservice.extensions import ma


class SampleRelationshipSchema(BaseSchema):
    parent_id = field_for(SampleRelationship, 'parent_id',
                          required=False,
                          load_only=True, example='SA_B048J5')
    child_id = field_for(SampleRelationship, 'child_id',
                         required=False,
                         load_only=True, example='SA_B048J6')

    class Meta(BaseSchema.Meta):
        model = SampleRelationship
        resource_url = 'api.sample_relationships'
        collection_url = 'api.sample_relationships_list'
        exclude = BaseSchema.Meta.exclude + ('child', 'parent')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'parent': PatchedURLFor('api.samples',
                            kf_id='<parent_id>'),
        'child': PatchedURLFor('api.samples',
                           kf_id='<child_id>')
    })


class SampleRelationshipFilterSchema(SampleRelationshipSchema):

    sample_id = fields.Str()

    @validates('sample_id')
    def valid_sample_id(self, value):
        validate_kf_id('SA', value)
