import os
import subprocess

from flask.views import MethodView

from dataservice.utils import _get_version
from dataservice.api.common.schemas import StatusSchema


class StatusAPI(MethodView):
    """
    Service Status
    """
    def get(self):
        """
        Get the service status

        Returns information about the current API's version and status
        """
        commit = (subprocess.check_output(
                  ['git', 'rev-parse', '--short', 'HEAD'])
                  .decode("utf-8").strip())

        tags = (subprocess.check_output(
                ['git', 'tag', '-l', '--points-at', 'HEAD'])
                .decode('utf-8').split('\n'))
        tags = [] if tags[0] == '' else tags
        resp = {
                'message': 'Welcome to the Kids First Dataservice API',
                'code': 200,
                'version': _get_version(),
                'commit': commit,
                'tags': tags
        }
        return StatusSchema().jsonify(resp)
