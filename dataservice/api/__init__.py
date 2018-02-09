from flask import Blueprint
from dataservice.api.docs import Documentation, Swagger
from dataservice.api.status import StatusAPI

from dataservice.api.common.views import CRUDView
from dataservice.api.participant import ParticipantAPI
from dataservice.api.participant import ParticipantListAPI


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

views = CRUDView.register_views(api)

# Sample resource
#register_crud_resource(api, SampleAPI, 'samples', '/samples/')
