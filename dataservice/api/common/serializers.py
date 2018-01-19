from datetime import datetime
from flask_restplus import Model, fields

# Fields that exist in all entities
base_entity = Model('BaseFields', {
    'kf_id': fields.String(
        example='ABCD1234',
        description='ID assigned by Kids First'),
    'created_at': fields.String(
        example=datetime.now().isoformat(),
        description='Date Participant was registered in with the DCC'),
    'modified_at': fields.String(
        example=datetime.now().isoformat(),
        description='Date of last update to the Participants data')
})

_status_fields = Model('Status', {
    'message': fields.String(
        example='Success',
        description='Status message from the server'),
    'code': fields.Integer(
        example=200,
        description='HTTP status code from the server')
})

# Fields that exist on all responses
base_response = Model('BaseResponse', {
    '_status': fields.Nested(_status_fields)
})

_paginate_fields = Model('PaginateFields', {
    'next': fields.String(
        example='/participants?page=3',
        description='Location of the next page'),
    'self': fields.String(
        example='/participants?page=2',
        description='Location of the current page'),
    'prev': fields.String(
        example='/participants?page=1',
        description='Location of the previous page')
})

# Fields for paginated responses
base_pagination = base_response.clone('BasePagination', {
    '_links': fields.Nested(_paginate_fields)
})

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
