from flask import Blueprint
from dataservice.api.docs import Documentation, Swagger
from dataservice.api.status import StatusAPI

from dataservice.api.common.views import CRUDView
from dataservice.api.participant import ParticipantAPI
from dataservice.api.participant import ParticipantListAPI
from dataservice.api.diagnosis import DiagnosisAPI
from dataservice.api.diagnosis import DiagnosisListAPI
from dataservice.api.sample import SampleAPI
from dataservice.api.sample import SampleListAPI
from dataservice.api.demographic import DemographicAPI
from dataservice.api.demographic import DemographicListAPI
from dataservice.api.genomic_file import GenomicFileAPI
from dataservice.api.genomic_file import GenomicFileListAPI

from dataservice.api.study.models import Study


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

# All CRUD resources
views = CRUDView.register_views(api)
