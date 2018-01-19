from flask_restplus import fields

from dataservice.api.common.serializers import (
    _status_fields,
    base_response
)

_version_fields = _status_fields.clone('VersionFields', {
    'version': fields.String(
        example='/persons?page=3',
        description='Location of the next page'),
    'commit': fields.String(
        example='23cf525',
        description='Commit currently deployed'),
    'tags': fields.List(fields.String(
        example='rc-0.8.4',
        description='Any tags on the current commit'))
})

# Version response model
version_response = base_response.clone('VersionResponse', {
    '_status': fields.Nested(_version_fields)
})
