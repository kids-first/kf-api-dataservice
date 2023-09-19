from typing import Optional, Tuple
from datetime import datetime
from uuid import UUID
from dataservice.extensions import ma
from marshmallow import (
    fields,
    post_load,
    post_dump,
    pre_dump,
    validates_schema,
    validates,
    ValidationError
)
from flask import url_for, request
from flask_marshmallow import Schema
from dataservice.api.common.pagination import Pagination, After
from dataservice.api.common.validation import validate_kf_id
from dataservice.api.common.model import VISIBILITY_REASON_ENUM
from dataservice.extensions import db

AVAILABILITY_ENUM = {'Immediate Download',
                     'Cold Storage'}


def format_after(after: Optional[After]) -> Tuple[float, str]:
    # epoch and 0 uuid are synonymous with no after param, return none
    # as it's most likely the user came from the root endpoint
    if after is None or after == (datetime.fromtimestamp(0), str(UUID(int=0))):
        return None, None
    return after[0].timestamp(), after[1]


class BaseSchema(ma.ModelSchema):

    __pagination__ = None

    def __init__(self, code=200, message='success', *args, **kwargs):
        self.status_code = code
        self.status_message = message
        # Add the request's db session to serializer if one is not specified
        if 'session' not in kwargs:
            kwargs['session'] = db.session
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

    @validates('kf_id')
    def valid(self, value):
        validate_kf_id(self.Meta.model.__prefix__, value)

    @validates('visibility_reason')
    def validate_visibility_reason(self, value):
        if value and (value not in VISIBILITY_REASON_ENUM):
            raise ValidationError(
                'Not a valid choice. Must be one of: {}'.format(
                    ', '.join([str(item) for item in VISIBILITY_REASON_ENUM]))
            )

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

            after_date, after_uuid = format_after(p.curr_num)
            _links['self'] = url_for(self.Meta.collection_url,
                                     after=after_date,
                                     after_uuid=after_uuid,
                                     study_id=request.args.get('study_id'))
            if p.has_next:
                next_date, next_uuid = format_after(p.next_num)
                _links['next'] = url_for(self.Meta.collection_url,
                                         after=next_date,
                                         after_uuid=next_uuid,
                                         study_id=request.args.get('study_id'))
            resp['total'] = int(p.total)
            resp['limit'] = int(p.limit)
        else:
            _links = {}

        resp.update({'results': data,
                     '_links': _links})
        return resp

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        if data is None:
            return
        if type(original_data) is list:
            unknown = (set([o for obj in original_data for o in obj]) -
                       set(self.fields))
        else:
            unknown = set(original_data) - set(self.fields)
        if unknown:
            raise ValidationError('Unknown field', unknown)


def acl_deprecation(val):
    """
    Ensure that user is not populating the ACL field. ACL field can only be an
    empty list

    If ACL field is not a list, this will be caught marshmallow type validation
    Therefore, only check if ACL field contains a non-empty list and raise
    an exception if it is not
    """
    if isinstance(val, list) and len(val) > 0:
        raise ValidationError(
            "The ACL field has been deprecated. "
            "Please use the authz field instead"
        )


class IndexdFileSchema(Schema):
    urls = ma.List(ma.Str(), required=True)
    access_urls = ma.List(ma.Str(), dump_only=True)
    acl = ma.List(ma.Str(), required=False)
    authz = ma.List(ma.Str(), required=False)
    file_name = ma.Str()
    hashes = ma.Dict(required=True)
    metadata = ma.Dict(attribute='_metadata')
    size = ma.Int(required=True)


class ErrorSchema(Schema):
    """ Handles HTTPException marshalling """

    class Meta:
        fields = ("description", "code")

    @post_dump(pass_many=False)
    def wrap_envelope(self, data):
        return {'_status': {'message': data['description'],
                            'code': data['code']}}


def error_response_generator(status_code):
    class ErrorResponseSchema(Schema):
        _examples = {
            404: "could not find <entity> <entity.kf_id>",
            400: ("could not <create | update> <entity>"
                  " {'<field>': ['Not a valid <expected type>.']}")
        }
        description = fields.String(description='status message',
                                    example=_examples.get(status_code))
        code = fields.Integer(description='HTTP response code',
                              example=status_code)

    return ErrorResponseSchema


def response_generator(schema):
    class RespSchema(Schema):
        _status = fields.Dict(example={'message': 'success', 'code': 200})
        results = fields.Nested(schema)

    return RespSchema


def paginated_generator(url, schema):

    class PaginatedSchema(Schema):
        _status = fields.Dict(example={'message': 'success', 'code': 200})
        _links = fields.Dict(
            example={'next': '{}?after=1519402953'.format(url),
                     'self': '{}?after=1519402952'.format(url)
                     })
        limit = fields.Integer(example=10,
                               description='Max number of results per page')
        total = fields.Integer(example=1342,
                               description='Total number of results')
        results = fields.List(fields.Nested(schema))

    return PaginatedSchema


def filter_schema_factory(model_schema_cls):
    """
    Create an instance of a model's filter schema

    Dynamically define filter schemas based on model schema
    and filter schema mixin classes
    Remove schema attributes that are not applicable to filters (_links)
    Allow partially populated schema
    Validate with strict=True - reuse model schema's validators
    """

    # Dynamically define the model filter schema class
    cls_name = ('{}FilterSchema'
                .format(model_schema_cls.__name__.split('Schema')[0]))
    base_classes = (FilterSchemaMixin, model_schema_cls)
    cls = type(cls_name, base_classes, {})

    # Update some class attributes
    exclude = ('_links', )
    if hasattr(cls.Meta, 'exclude'):
        exclude += cls.Meta.exclude

    # Generate class instance
    return cls(strict=True, partial=True, exclude=exclude)


class FilterSchemaMixin(ma.Schema):
    """
    Filter schema mixin inherited by all model filter schemas
    """
    study_id = fields.Str()

    class Meta:
        dump_only = ()

    @validates('study_id')
    def valid_study_id(self, value):
        validate_kf_id('SD', value)

    @post_load
    def make_instance(self, data):
        return data


class StatusSchema(Schema):

    message = fields.String(description='status message', example='success')
    code = fields.Integer(description='HTTP response code', example=200)
    version = fields.Str(description='API version number', example='1.2.0')
    commit = fields.Str(description='API short commit hash', example='aef3b5a')
    branch = fields.Str(description='API branch name', example='master')
    tags = fields.List(
        fields.String(description='Any tags associated with the version',
                      example=['rc', 'beta']))

    @post_dump(pass_many=False)
    def wrap_envelope(self, data):
        return {'_status': data}
