from flask import Blueprint
from dataservice.api.participant import ParticipantAPI


def register_crud_resource(app, view, endpoint, url, pk='kf_id', pk_type='string'):
    """
    Registers a crud resource with the following endpoints:
    GET    /<url>/
    POST   /<url>/
    GET    /<url>/<kf_id>
    PUT    /<url>/<kf_id>
    DELETE /<url>/<kf_id>

    From the flask docs:
    http://flask.pocoo.org/docs/0.12/views/#method-views-for-apis
    """
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('{}<{}:{}>'.format(url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

api = Blueprint('api', __name__, url_prefix='')

register_crud_resource(api, ParticipantAPI, 'participants', '/participants/')


from dataservice.api.common.schemas import BaseStatus
@api.errorhandler(404)
def not_found(e):
    return BaseStatus().jsonify(e), 404
