from dataservice.extensions import ma
from marshmallow import (
        fields,
        post_dump,
        validates_schema,
        ValidationError
)
from flask_marshmallow import Schema


class BaseSchema(ma.ModelSchema):

    def __init__(self, code=200, message='success', *args, **kwargs):
        self.status_code = code
        self.status_message = message
        super(BaseSchema, self).__init__(*args, **kwargs)

    class Meta:
        exclude = ('uuid',)
        dump_only = ('created_at', 'modified_at')

    @post_dump(pass_many=True)
    def wrap_envelope(self, data, many):
        if not many and '_links' in data:
            _links = data['_links']
            del data['_links']
        else:
            _links = {}

        return {'results': data,
                '_links': _links,
                '_status': {'message': self.status_message,
                            'code': self.status_code}}

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise ValidationError('Unknown field', unknown)


class ErrorSchema(Schema):
    """ Handles HTTPException marshalling """

    class Meta:
        fields = ('description', 'code')

    @post_dump(pass_many=False)
    def wrap_envelope(self, data):
        return {'_status': {'message': data['description'],
                            'code': data['code']}}


def response_generator(schema):
    class RespSchema(Schema):
        _status = fields.Dict(example={'message': 'success', 'code': 200})
        results = fields.Nested(schema)

    return RespSchema


def paginated_generator(schema):
    class PaginatedSchema(Schema):
        _status = fields.Dict(example={'message': 'success', 'code': 200})
        _links = fields.Dict(example={'next': '?page=3',
                                      'self': '?page=2',
                                      'prev': '?page=1'})
        limit = fields.Integer(example=10,
                               description='Max number of results per page')
        total = fields.Integer(example=1342,
                               description='Total number of results')
        results = fields.List(fields.Nested(schema))

    return PaginatedSchema


class StatusSchema(Schema):

    message = fields.String(description='status message', example='success')
    code = fields.Integer(description='HTTP response code', example=200)
    version = fields.Str(description='API version number', example='1.2.0')
    commit = fields.Str(description='API short commit hash', example='aef3b5a')
    tags = fields.List(
            fields.String(description='Any tags associated with the version',
                          example=['rc', 'beta']))

    @post_dump(pass_many=False)
    def wrap_envelope(self, data):
        return {'_status': data}
