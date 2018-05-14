import re
from marshmallow import ValidationError
from marshmallow.validate import OneOf, Validator

from marshmallow.fields import Str

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


class FieldValidator(Str):
    """
    Custom Field Validator to take field_name in the validation
    """

    def _validate(self, value):
        """Perform validation on ``value``. Raise a :exc:`ValidationError`
        if validation
        does not succeed.
        """
        errors = []
        kwargs = {}
        for validator in self.validators:
            try:
                try:
                    r = validator(value, field=self)
                except TypeError:
                    # This validator does not accept the field instance
                    r = validator(value)
                if not isinstance(validator, Validator) and r is False:
                    self.fail('validator_failed')
            except ValidationError as err:
                kwargs.update(err.kwargs)
                if isinstance(err.messages, dict):
                    errors.append(err.messages)
                else:
                    errors.extend(err.messages)
        if errors:
            raise ValidationError(errors, **kwargs)


def validate_ontology_id_prefix(attribute, field):
    """
    Validates a ontolgy column id with prefix
    """
    prefix = field.attribute.split('_')[0]
    onto_dict = {
        'mondo': 'MONDO:',
        'uberon': 'UBERON:',
        'icd':	'ICD10:',
        'hpo':	'HP:',
        'snomed': 'SNOMEDCT:',
        'ncit': 'NCIT:'
    }
    if attribute is not None:
        if attribute.startswith(onto_dict[prefix]) is False:
            raise ValidationError('Must have prefix {}'.format(
                onto_dict[prefix]))
