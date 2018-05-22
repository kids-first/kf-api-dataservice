from marshmallow_sqlalchemy import field_for

from dataservice.api.phenotype.models import Phenotype
from dataservice.api.common.schemas import BaseSchema, COMMON_ENUM
from dataservice.api.common.validation import (validate_age,
                                               enum_validation_generator)
from dataservice.extensions import ma
from marshmallow import post_dump

OBSERVED_ENUM = {'positive': 'Positive', 'negative': 'Negative'}
OBSERVED_ENUM.update(COMMON_ENUM)


class PhenotypeSchema(BaseSchema):

    participant_id = field_for(Phenotype, 'participant_id', required=True,
                               load_only=True, example='PT_DZB048J5')
    age_at_event_days = field_for(Phenotype, 'age_at_event_days',
                                  validate=validate_age, example=232)
    observed = field_for(Phenotype, 'observed',
                         validate=enum_validation_generator(
                             OBSERVED_ENUM))

    @post_dump()
    def auto_populate_enum(self, data):
        if data['observed'] is not None:
            data['observed'] = OBSERVED_ENUM[data['observed'].lower()]

    class Meta(BaseSchema.Meta):
        model = Phenotype
        resource_url = 'api.phenotypes'
        collection_url = 'api.phenotypes_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
