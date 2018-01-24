from dataservice.extensions import ma
from marshmallow import post_dump, post_load, validates_schema, ValidationError
from flask_marshmallow import Schema


class BaseSchema(ma.ModelSchema):

    def __init__(self, code=200, message='success', *args, **kwargs):
        self.status_code = code
        self.status_message = message
        super(BaseSchema, self).__init__(*args, **kwargs)

    class Meta:
        exclude = ('_id', 'uuid')
        dump_only = ('created_at', 'modified_at')

    @post_dump(pass_many=True)
    def wrap_envelope(self, data, many):
        if type(data) is not list:
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


class StatusSchema(Schema):

    class Meta:
        fields = ('message', 'code', 'version', 'commit', 'tags')

    @post_dump(pass_many=False)
    def wrap_envelope(self, data):
        return {'_status': data}
