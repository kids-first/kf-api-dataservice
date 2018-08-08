from marshmallow_sqlalchemy import field_for
from dataservice.api.family.models import Family
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma
from dataservice.api.common.validation import (enum_validation_generator)
FAMILY_TYPE_ENUM = {"Proband Only", "Duo", "Duo+",
                    "Trio", "Trio +", "Other", }


class FamilySchema(BaseSchema):
    family_type = field_for(Family, 'family_type',
                            validate=enum_validation_generator(
                                FAMILY_TYPE_ENUM))

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
