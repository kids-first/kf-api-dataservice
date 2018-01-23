from dataservice.api.common.schemas import ErrorSchema


def http_error(e):
    """ Handles all HTTPExceptions """
    return ErrorSchema().jsonify(e), e.code
