from flask_restplus import Api
from .person import person_api

api = Api(title='Kids First Data Service',
          description=open('dataservice/api/README.md').read(),
          version='0.1',
          default='',
          default_label='')

api.add_namespace(person_api)


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
