import re
from dataservice.api.common.schemas import ErrorSchema
from dataservice.extensions import db


FOREIGN_KEY_RE = re.compile('.*\nDETAIL:.*\((?P<kf_id>.*)\)' +
                            ' is not present in table "(?P<table>\w+)"\.')

UNIQUE_RE = re.compile('^.*"(?P<key>.*)_key"\n' +
                       'DETAIL:.*\((?P<entity>\w+)_id\)=' +
                       '\((?P<kf_id>.*)\) already exists\.')


def http_error(e):
    """ Handles all HTTPExceptions """
    return ErrorSchema().jsonify(e), e.code


def integrity_error(e):
    """
    Handles IntegrityError exceptions raised by SQLAlchemy.
    String parsing assumes errors are reported from PostgreSQL and won't
    work if using a different backend.
    """
    db.session.rollback()
    error = e.orig.pgerror

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
        key = key.replace('_' + m.group('entity')+'_id', '')
        message = '{} "{}" may only have one {}'.format(m.group('entity'),
                                                        m.group('kf_id'),
                                                        key)

    resp = {'code': 400, 'description': message}
    return ErrorSchema().jsonify(resp), 400
