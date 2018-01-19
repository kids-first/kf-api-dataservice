import pkg_resources
import subprocess
from flask import Blueprint
from flask_restplus import Api
from dataservice.api.participant import participant_api

api_v1 = Blueprint('api', __name__, url_prefix='')

api = Api(api_v1,
          title='Kids First Data Service',
          description=open('dataservice/api/README.md').read(),
          version=_get_version(),
          default='',
          default_label='')

api.add_namespace(participant_api)


@api.route("/status")
class Status(Resource):
    """
    Service Status
    """
    @api.marshal_with(version_response)
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


@api.documentation
def redoc_ui():
    """ Uses ReDoc for swagger documentation """
    docs_page = """<!DOCTYPE html>
    <html>
    <head>
    <title>API Docs</title>
    <!-- needed for mobile devices -->
    <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
    <redoc spec-url="{}"></redoc>
    <script src="https://rebilly.github.io/ReDoc/releases/latest/redoc.min.js">
    </script>
    </body>
    </html>
    """.format(api.specs_url)
    return docs_page
