from flask import Blueprint
from dataservice.api.status import StatusAPI
from dataservice.api.participant import ParticipantAPI


def register_crud_resource(app, view, endpoint, url,
                           pk='kf_id', pk_type='string'):
    """
    Registers a crud resource with the following endpoints:
    GET    /<url>/
    POST   /<url>/
    GET    /<url>/<kf_id>
    PUT    /<url>/<kf_id>
    DELETE /<url>/<kf_id>


    :param app: the flask application or blueprint
    :param view: the View or MethodView to define rules for
    :param endpoint: the name of the endpoint
    :param rule: the desired url with trailing `/`
    :param pk: the primary key used as an argument to the View's routes
    :param pk_type: the type of the primary key

    From the flask docs:
    http://flask.pocoo.org/docs/0.12/views/#method-views-for-apis
    """
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET'])
    app.add_url_rule(url, view_func=view_func, methods=['POST'])
    app.add_url_rule('{}<{}:{}>'.format(url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

api = Blueprint('api', __name__, url_prefix='')

# Status resource
status_view = StatusAPI.as_view('status')
api.add_url_rule('/', view_func=status_view, methods=['GET'])
api.add_url_rule('/status', view_func=status_view, methods=['GET'])
# Participant resource
register_crud_resource(api, ParticipantAPI, 'participants', '/participants/')
