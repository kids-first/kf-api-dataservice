import re
from flask import current_app
from dataservice.api.common.schemas import ErrorSchema
from dataservice.extensions import db

FOREIGN_KEY_RE = re.compile('.*\nDETAIL:.*\((?P<kf_id>.*)\)' +
                            ' is not present in table "(?P<table>\w+)"\.')

UNIQUE_RE = re.compile('^.*"(?P<key>.*)_key"\n' +
                       'DETAIL:.*\((?P<entity>\w+)_id\)=' +
                       '\((?P<kf_id>.*)\) already exists\.')
UNIQUE_COL_RE = re.compile('duplicate key value violates unique constraint ' +
                           '"(?P<table>\w+)"\n' +
                           'DETAIL:.*\((?P<column>\w+)\)=' +
                           '\((?P<value>.*)\) already exists\.\n')


class DatabaseValidationError(Exception):

    def __init__(self, target_entity, operation, message=None):
        super().__init__(self, target_entity, operation, message)
        self.target_entity = target_entity
        self.operation = operation
        self.message = message or 'error saving changes'


def database_validation_error(e):
    db.session.rollback()
    data = {
        'description': 'could not {} {}: {}'.format(e.operation,
                                                    e.target_entity,
                                                    e.message),
        'code': 400
    }
    return ErrorSchema().jsonify(data), data['code']


def http_error(e):
    """
    Handles all HTTPExceptions

    HTTP 422 Unprocessable Entity exceptions result from validation errors in
    processing filter parameters. The message from the 422 error must be
    parsed differently than other HTTP errors
    """
    db.session.rollback()
    # Default message
    data = e
    code = e.code

    # HTTP 422 message
    if e.code == 422:
        data, code = handle_filter_validation_error(e)
    return ErrorSchema().jsonify(data), code


def handle_filter_validation_error(e):
    """
    Parse UnprocessableEntity exceptions resulting from
    filter parameter validation errors.
    """
    code = 400
    message = 'could not retrieve entities:'
    data = {'description': '{} {}'.format(message, e.exc.messages),
            'code': code}
    return data, code


def integrity_error(e):
    """
    Handles IntegrityError exceptions raised by SQLAlchemy.
    String parsing assumes errors are reported from PostgreSQL and won't
    work if using a different backend.
    """
    db.session.rollback()
    error = e.orig.pgerror
    current_app.logger.debug(error)

    message = 'error saving changes'

    m = FOREIGN_KEY_RE.match(error)
    # Tried to create entity, but another entity must be created first
    if m and 'kf_id' in m.groups():
        message = 'A {} must be created first'.format(m.group('table'))
    # Tried to create an entity dependent on an entity that doesn't exist
    elif m:
        message = '{} "{}" does not exist'.format(m.group('table'),
                                                  m.group('kf_id'))

    m = UNIQUE_RE.match(error)
    # Entity is related to other entity already
    if m:
        key = m.group('key')
        key = key.replace('_' + m.group('entity') + '_id', '')
        message = '{} "{}" may only have one {}'.format(m.group('entity'),
                                                        m.group('kf_id'),
                                                        key)
    # Tried to create row with same value in column
    m = re.findall(UNIQUE_COL_RE, error)
    if m:
        table = m[0][0]
        l = table.split('_')
        # The last two elements in list are column_name and key
        if len(l) == 4:
            table = '_'.join(l[:2])
        else:
            table = l[:1]
        column = m[0][1]
        value = m[0][2]
        message = ("could not create {0}. {0} with {1} = '{2}' already exists."
                   .format(table, column, value))

    resp = {'code': 400, 'description': message}
    return ErrorSchema().jsonify(resp), 400
