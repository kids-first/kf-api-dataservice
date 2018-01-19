from flask import Blueprint
from flask_restplus import Api
from dataservice.api.participant import participant_api
from dataservice.api.status import status_api
from dataservice.utils import _get_version

api_v1 = Blueprint('api', __name__, url_prefix='')

api = Api(api_v1,
          title='Kids First Data Service',
          description=open('dataservice/api/README.md').read(),
          version=_get_version(),
          default='',
          default_label='')

api.add_namespace(status_api)
api.add_namespace(participant_api)


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
