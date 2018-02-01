from dataservice.api.common.schemas import ErrorSchema

FOREIGN_KEY_ERROR_PREFIX = 'foreign key constraint failed'
FOREIGN_KEY_ERROR_MSG_TEMPLATE = \
    'Cannot {} {} without an existing {} entity'

UNIQUE_CONSTRAINT_ERROR_PREFIX = 'unique constraint failed'
UNIQUE_CONSTRAINT_ERROR_MSG_TEMPLATE = \
    'Cannot {0} {1}, {2} already has a {1}'

DEFAULT_INVALID_INPUT_TEMPLATE = 'Client error: invalid {} provided'


def http_error(e):
    """ Handles all HTTPExceptions """
    return ErrorSchema().jsonify(e), e.code


def handle_integrity_error(**kwargs):
    """
    Handle invalid client input error

    Determine error type based on error kwargs
    Return message based on kwargs
    """
    # Default error message
    message = DEFAULT_INVALID_INPUT_TEMPLATE.format(kwargs.get('entity'))

    # Extract type of error from exception message
    error_type = str(kwargs.get('exception').orig).strip().lower()
    method = kwargs.get('method')
    entity = kwargs.get('entity')
    ref_entity = kwargs.get('ref_entity')

    # Foreign key constraint failed
    if FOREIGN_KEY_ERROR_PREFIX in error_type:
        message = FOREIGN_KEY_ERROR_MSG_TEMPLATE.\
            format(method, entity, ref_entity)

    # Unique constraint failed
    elif UNIQUE_CONSTRAINT_ERROR_PREFIX in error_type:
        message = UNIQUE_CONSTRAINT_ERROR_MSG_TEMPLATE.\
            format(method, entity, ref_entity)

    return message
