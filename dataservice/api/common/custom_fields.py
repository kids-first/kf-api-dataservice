from dateutil import parser
from marshmallow import (
    fields,
    ValidationError
)

from flask import url_for
from flask_marshmallow.fields import (
    _tpl,
    get_value,
    missing,
    iteritems
)

from dataservice.extensions import ma


class PatchedURLFor(ma.URLFor):
    """
    Patched version of flask_marshmallow's URLFor field. Original version
    has a bug that throws a werkzeug BuildError when `id` is None.
    Patched version accepts the `allow_none` kwarg. When `allow_none` = True
    the URLFor will serialize to None.

    Original Documentation for flask_marshmallow.URLFor:
    Field that outputs the URL for an endpoint. Acts identically to
    Flask's ``url_for`` function, except that arguments can be pulled from the
    object to be serialized.

    Usage: ::

        url = URLFor('author_get', id='<id>')
        https_url = URLFor('author_get', id='<id>', _scheme='https',
        _external=True)

    :param str endpoint: Flask endpoint name.
    :param kwargs: Same keyword arguments as Flask's url_for, except string
        arguments enclosed in `< >` will be interpreted as attributes to pull
        from the object.
    """

    def __init__(self, endpoint, **kwargs):
        super().__init__(endpoint, **kwargs)

    def _serialize(self, value, key, obj):
        """Output the URL for the endpoint, given the kwargs passed to
        ``__init__``.
        """
        param_values = {}
        for name, attr_tpl in iteritems(self.params):
            attr_name = _tpl(str(attr_tpl))
            if attr_name:
                attribute_value = get_value(obj, attr_name, default=missing)

                allow_none = self.params.get('allow_none', True)
                if allow_none and (attribute_value is None):
                    return None

                if attribute_value is not missing:
                    param_values[name] = attribute_value
                else:
                    raise AttributeError(
                        '{attr_name!r} is not a valid '
                        'attribute of {obj!r}'.format(attr_name=attr_name,
                                                      obj=obj)
                    )
            else:
                param_values[name] = attr_tpl
        return url_for(self.endpoint, **param_values)


class DateOrDatetime(fields.DateTime):
    """
    Custom field that represents a date/datetime field
    Provide flexible deserialization by allowing values
    that are either Date or DateTime objects

    * NOTE - Marshmallow's _deserialize method assumes an iso
    formatted datetime string (if a format is not passed into the fields
    constructor). Unfortunately, if the parsing fails, marshmallow does not
    continue to try parsing the string with dateutil. It just raises a
    ValidationError.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data):
        """
        Convert from string to datetime object
        """
        try:
            value = parser.parse(str(value)) if value else None
        except ValueError as e:
            raise ValidationError('Invalid date or datetime string')

        return value
