from dataservice.api.common.schemas import BaseStatus


def http_error(e):
    """ Handles all HTTPExceptions """
    return BaseStatus().jsonify(e), e.code
