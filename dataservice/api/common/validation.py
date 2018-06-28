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


class EnumValidator(OneOf):
    """
    Modified OneOf validator class to provide case sensitive or insensitive
    enumeration validation. Use kwarg `ignore_case` to set whether case
    should be taken into account in validation. Set to True by default.
    Original documentation:
    Validator which succeeds if ``value`` is a member of ``choices``.
    :param iterable choices: A sequence of valid values.
    :param iterable labels: Optional sequence of labels to pair with the
    choices.
    :param str error: Error message to raise in case of a validation error.
    Can be interpolated with `{input}`, `{choices}` and `{labels}`.
    """

    default_message = 'Not a valid choice.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ignore_case = kwargs.get('ignore_case', True)

    def __call__(self, orig_value):
        value = orig_value
        choices = {v: v for v in self.choices}
        if self.ignore_case:
            if type(value) is str:
                value = orig_value.lower()
                choices = {choice.lower(): choice for choice in self.choices}
            else:
                value = str(value)
        try:
            if value not in choices:
                raise ValidationError(self._format_error(orig_value))
        except TypeError:
            raise ValidationError(self._format_error(orig_value))
        return choices[value]


def enum_validation_generator(_enum, common=True):

    error_message = 'Not a valid choice. Must be one of: {}'.format(
        ', '.join(list(_enum)))
    return EnumValidator(_enum, error=error_message)
