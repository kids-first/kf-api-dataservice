from flask import Blueprint
from dataservice.api.participant import ParticipantAPI


def register_api(app, view, endpoint, url, pk='kf_id', pk_type='string'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

api = Blueprint('api', __name__, url_prefix='')

register_api(api, ParticipantAPI, 'participant_api', '/participants')
