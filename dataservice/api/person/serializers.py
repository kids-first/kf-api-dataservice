from flask_restplus import fields

from dataservice.api.common.serializers import (
    base_entity,
    base_response,
    base_pagination,
    _status_fields,
    _paginate_fields
)
from dataservice.api.person.resources import person_api


person_api.models['Status'] = _status_fields
person_api.models['PaginateFields'] = _paginate_fields

# Fields unique to a Person, used as the new person request model
person_fields = person_api.model('PersonFields', {
    'external_id': fields.String(
        example='SUBJ-3993',
        description='Identifier used in the original study data')
})

person_model = person_api.clone('Person', base_entity, person_fields)

person_list = person_api.clone("PersonsList", base_pagination, {
    "results": fields.List(fields.Nested(person_model))
})

person_response = person_api.clone('PersonResponse', base_response, {
    'results': fields.Nested(person_model)
})
