import re
from marshmallow import ValidationError
from marshmallow.validate import OneOf

MIN_AGE_DAYS = 0
# Max value chosen due to HIPAA de-identification standard
# Using safe harbor guidelines
# Equates to 90 years
MAX_AGE_DAYS = 32872


def validate_age(value):
    """
    Validates a relative age in days

    Age at the time of an event, expressed in number of days since birth
    """
    if value < MIN_AGE_DAYS:
        raise ValidationError('Age must be an integer greater than {}.'
                              .format(MIN_AGE_DAYS))
    if value > MAX_AGE_DAYS:
        raise ValidationError('Age must be an integer less than {}.'
                              .format(MAX_AGE_DAYS))


def validate_positive_number(value):
    """
    Validates a that value is a positive number
    """
    type_str = type(value).__name__
    if int(value) < 0:
        raise ValidationError('Must be a positive {}'.format(type_str))


def validate_kf_id(prefix, value):
    r = r'^' + prefix + r'_[A-HJ-KM-NP-TV-Z0-9]{8}'
    m = re.search(r, value)
    if not m:
        raise ValidationError('Invalid kf_id')


def enum_validation_generator(_enum, common=True):
    from dataservice.api.common.model import COMMON_ENUM

    extended_enum = _enum.union(COMMON_ENUM) if common else _enum
    error_message = 'Not a valid choice. Must be one of: {}'.format(
        ', '.join([str(el) for el in extended_enum]))

    return OneOf(extended_enum, error=error_message)


def list_validation_generator(valid_items, items_name='items'):
    """
    Return a list validation function

    :param valid_items: valid collection of items to use in validation
    :type valid_items: list
    :items_name: the plural identifier of an item in the list. Used in the
    ValidationError message

    :returns: the validate_list method
    """
    def validate_list(input_items):
        """
        Check whether all items in the input list exist in another list
        representing the collection of valid values.

        All list items are converted to strings before
        doing comparison and validation.

        ** NOTE **
        This method is used by marshmallow_sqlalchemy.field_for during
        HTTP request validation. If the HTTP request method is GET,
        `input_items` will be a list with one element which will be a delimited
        string representing a list of strings
        (e.g. ['duo:0000005,duo:0000001']). This is because the value comes
        from the URL query parameter string. No need to validate this case.

        :param input_items: input collection of items to validate
        :type input_items: list or str
        :raises: ValidationError when validation fails
        """
        assert isinstance(input_items, list), (
            'Parameter `input_items` must be a list'
        )
        # Don't do validation for this case, just return. See NOTE in docstring
        if len(input_items) == 1 and any([d in input_items[0]
                                          for d in [',', ' ', ';']]):
            return

        invalid_set = set(input_items) - set(valid_items)

        if invalid_set:
            raise ValidationError(
                f'The following {items_name} are invalid: '
                f'{", ".join(invalid_set)}. All {items_name} must be in the '
                f'valid set: {", ".join(valid_items)}'
            )
    return validate_list
