from flask import current_app
from flask.views import MethodView

from dataservice.api.common.schemas import StatusSchema


class StatusAPI(MethodView):
    """
    Service Status
    """
    def get(self):
        """
        Get the service status

        Returns information about the current API's version and status
        ---
        description: Get the service status
        tags:
        - "Status"
        responses:
            200:
                description: Success
                schema:
                    $ref: '#/definitions/Status'
        """
        resp = {
                'message': 'Welcome to the Kids First Dataservice API',
                'code': 200,
                'version': current_app.config['PKG_VERSION'],
                'commit': current_app.config['GIT_COMMIT'],
                'branch': current_app.config['GIT_BRANCH'],
                'tags': current_app.config['GIT_TAGS'],
                'datamodel': current_app.config['MODEL_VERSION'],
                'migration': current_app.config['MIGRATION'],
        }
        return StatusSchema().jsonify(resp)
