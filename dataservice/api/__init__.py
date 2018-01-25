from flask import Blueprint
from dataservice.api.docs import Documentation, Swagger
from dataservice.api.status import StatusAPI
from dataservice.api.participant import ParticipantAPI
from dataservice.api.participant import ParticipantListAPI
from dataservice.api.demographic import DemographicAPI
from dataservice.api.diagnosis import DiagnosisAPI
from dataservice.api.diagnosis import DiagnosisListAPI
from dataservice.api.sample import SampleAPI
from dataservice.api.demographic import DemographicAPI
from dataservice.api.diagnosis import DiagnosisAPI


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
    return view_func

api = Blueprint('api', __name__, url_prefix='', template_folder='templates')

# Documentation
docs_view = Documentation.as_view('docs')
swagger_view = Swagger.as_view('swagger')
api.add_url_rule('/', view_func=docs_view, methods=['GET'])
api.add_url_rule('/docs', view_func=docs_view, methods=['GET'])
api.add_url_rule('/swagger', view_func=swagger_view, methods=['GET'])

# Status resource
status_view = StatusAPI.as_view('status')
api.add_url_rule('/status', view_func=status_view, methods=['GET'])

# Participant resource
participant_list_view = ParticipantListAPI.as_view('participants_list')
api.add_url_rule('/participants',
                 view_func=participant_list_view,
                 methods=['GET', 'POST'])

participant_view = ParticipantAPI.as_view('participants')
api.add_url_rule('/participants/<string:kf_id>',
                 view_func=participant_view,
                 methods=['GET', 'PUT', 'DELETE'])

# Demographic resource
register_crud_resource(api, DemographicAPI, 'demographics', '/demographics/')

# Diagnosis resource
#register_crud_resource(api, DiagnosisAPI, 'diagnoses', '/diagnoses/')
diagnosis_list_view = DiagnosisListAPI.as_view('diagnoses_list')
api.add_url_rule('/diagnoses',
                 view_func=diagnosis_list_view,
                 methods=['GET', 'POST'])

diagnosis_view = DiagnosisAPI.as_view('diagnoses')
api.add_url_rule('/diagnoses/<string:kf_id>',
                 view_func=diagnosis_view,
                 methods=['GET', 'PUT', 'DELETE'])

# Sample resource
register_crud_resource(api, SampleAPI, 'samples', '/samples/')
