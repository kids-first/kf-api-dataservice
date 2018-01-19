import os
import subprocess

from flask_restplus import Namespace, Resource, fields

from dataservice.utils import _get_version

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
README_FILE = os.path.join(THIS_DIR, 'README.md')

status_api = Namespace(name='status', description=open(README_FILE).read())

from dataservice.api.status.serializers import (  # noqa
    version_response,
    _version_fields
)


status_api.models['VersionFields'] = _version_fields
status_api.models['VersionResponse'] = version_response


@status_api.route("/")
class Status(Resource):
    """
    Service Status
    """
    @status_api.marshal_with(version_response)
    def get(self):
        """
        Get the service status

        Returns information about the current API's version and status
        """
        commit = (subprocess.check_output(
                  ["git", "rev-parse", "--short", "HEAD"])
                  .decode("utf-8").strip())

        tags = (subprocess.check_output(
                ["git", "tag", "-l", "--points-at", "HEAD"])
                .decode("utf-8").split('\n'))
        tags = [] if tags[0] == "" else tags
        return {"_status": {
                    "message": "Welcome to the Kids First Dataservice API",
                    "code": 200,
                    "version": _get_version(),
                    "commit": commit,
                    "tags": tags
                }}
