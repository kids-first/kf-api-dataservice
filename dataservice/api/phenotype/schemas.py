from marshmallow_sqlalchemy import field_for

from dataservice.api.phenotype.models import Phenotype
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import (validate_age,
                                               enum_validation_generator,
                                               validate_ontology_id_prefix,
                                               FieldValidator)
from dataservice.extensions import ma


OBSERVED_ENUM = {'Positive', 'Negative'}


class PhenotypeSchema(BaseSchema):

    participant_id = field_for(Phenotype, 'participant_id', required=True,
                               load_only=True, example='PT_DZB048J5')
    age_at_event_days = field_for(Phenotype, 'age_at_event_days',
                                  validate=validate_age, example=232)
    observed = field_for(Phenotype, 'observed',
                         validate=enum_validation_generator(
                             OBSERVED_ENUM))
    hpo_id_phenotype = FieldValidator(
        attribute='hpo_id_phenotype',
        validate=validate_ontology_id_prefix)
    snomed_id_phenotype = FieldValidator(attribute='snomed_id_phenotype',
                                         validate=validate_ontology_id_prefix)

    class Meta(BaseSchema.Meta):
        model = Phenotype
        resource_url = 'api.phenotypes'
        collection_url = 'api.phenotypes_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
