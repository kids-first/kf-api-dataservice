from dateutil import parser

from marshmallow import (
    fields,
    ValidationError
)


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

    def _deserialize(self, value, attr, data):
        """
        Convert from string to datetime object
        """
        try:
            value = parser.parse(str(value)) if value else None
        except ValueError as e:
            raise ValidationError('Invalid date or datetime string')

        return value
