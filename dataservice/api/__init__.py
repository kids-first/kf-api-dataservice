from flask import Blueprint

from dataservice.api.docs import Documentation, Logo, Swagger
from dataservice.api.status import StatusAPI
from dataservice.api.common.views import CRUDView

from dataservice.api.study import StudyAPI
from dataservice.api.study import StudyListAPI
from dataservice.api.investigator import InvestigatorAPI
from dataservice.api.investigator import InvestigatorListAPI
from dataservice.api.participant import ParticipantAPI
from dataservice.api.participant import ParticipantListAPI
from dataservice.api.family import FamilyAPI
from dataservice.api.family import FamilyListAPI
from dataservice.api.cavatica_app import CavaticaAppAPI
from dataservice.api.cavatica_app import CavaticaAppListAPI
from dataservice.api.cavatica_task import CavaticaTaskAPI
from dataservice.api.cavatica_task import CavaticaTaskListAPI
from dataservice.api.cavatica_task_genomic_file import (
    CavaticaTaskGenomicFileAPI,
    CavaticaTaskGenomicFileListAPI
)
from dataservice.api.family_relationship import FamilyRelationshipAPI
from dataservice.api.family_relationship import FamilyRelationshipListAPI
from dataservice.api.diagnosis import DiagnosisAPI
from dataservice.api.diagnosis import DiagnosisListAPI
from dataservice.api.biospecimen import BiospecimenAPI
from dataservice.api.biospecimen import BiospecimenListAPI
from dataservice.api.outcome import OutcomeAPI
from dataservice.api.outcome import OutcomeListAPI
from dataservice.api.phenotype import PhenotypeAPI
from dataservice.api.phenotype import PhenotypeListAPI
from dataservice.api.sequencing_center import SequencingCenterAPI
from dataservice.api.sequencing_center import SequencingCenterListAPI
from dataservice.api.sequencing_experiment import SequencingExperimentAPI
from dataservice.api.sequencing_experiment import SequencingExperimentListAPI
from dataservice.api.study_file import StudyFileAPI
from dataservice.api.study_file import StudyFileListAPI
from dataservice.api.genomic_file import GenomicFileAPI
from dataservice.api.genomic_file import GenomicFileListAPI

from dataservice.api.study.models import Study


api = Blueprint('api', __name__, url_prefix='', template_folder='templates')

# Documentation
docs_view = Documentation.as_view('docs')
logo_view = Logo.as_view('logo')
swagger_view = Swagger.as_view('swagger')
api.add_url_rule('/', view_func=docs_view, methods=['GET'])
api.add_url_rule('/logo', view_func=logo_view, methods=['GET'])
api.add_url_rule('/docs', view_func=docs_view, methods=['GET'])
api.add_url_rule('/swagger', view_func=swagger_view, methods=['GET'])

# Status resource
status_view = StatusAPI.as_view('status')
api.add_url_rule('/status', view_func=status_view, methods=['GET'])

# All CRUD resources
views = CRUDView.register_views(api)
