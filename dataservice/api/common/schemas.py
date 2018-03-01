from dataservice.extensions import ma
from marshmallow import (
        fields,
        post_dump,
        pre_dump,
        validates_schema,
        ValidationError
)
from flask import url_for, request
from dataservice.api.common.pagination import Pagination
from flask_marshmallow import Schema


class BaseSchema(ma.ModelSchema):

    __pagination__ = None

    def __init__(self, code=200, message='success', *args, **kwargs):
        self.status_code = code
        self.status_message = message
        super(BaseSchema, self).__init__(*args, **kwargs)

    class Meta:
        exclude = ('uuid',)
        dump_only = ('created_at', 'modified_at')

    @pre_dump(pass_many=True)
    def wrap_pre(self, data, many):
        if isinstance(data, Pagination):
            self.__pagination__ = data
            return data.items
        return data

    @post_dump(pass_many=True)
    def wrap_envelope(self, data, many):
        """
        Wraps ORM objects in a standard response format

        If `many=False`, only one object is being returned and any `_links`
        that are in the data are moved out to the response's `_links`.

        If `many=True`, many objects are being returned and the top `_links`
        in the response will be populated with pagination details.
        """
        resp = {'_status': {'message': self.status_message,
                            'code': self.status_code}}
        # Move links to the envelope links if just a single object
        if not many and '_links' in data:
            _links = data['_links']
            del data['_links']
        # Insert pagination object, if there is one
        elif many and self.__pagination__ is not None:
            p = self.__pagination__

            _links = {}

            # If an 'after' param could not be parsed, don't include the param
            after = None if p.after.timestamp() == 0 else p.curr_num
            _links['self'] = url_for(self.Meta.resource_url,
                                     after=after)
            if p.has_next:
                _links['next'] = url_for(self.Meta.resource_url,
                                         after=p.next_num)
            resp['total'] = int(p.total)
            resp['limit'] = int(p.limit)
        else:
            _links = {}

        resp.update({'results': data,
                     '_links': _links})
        return resp

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
        _links = fields.Dict(example={'next': '/participants?after=1519402953',
                                      'self': '/participants?after=1519402952'
                                      })
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
