import boto3
import jinja2
import json
import yaml
from flask import request, current_app
from flask.views import MethodView
from dataservice.api.common.schemas import (
    response_generator,
    paginated_generator,
    error_response_generator
)
from dataservice.extensions import db


class CRUDView(MethodView):
    """
    Extends :class:`~flask.views.MethodView` with class attributes needed
    to properly register mashmallow schemas and url rules on the apispec
    swagger generator. Also supports loading common path descriptions
    via yaml templates.

    :param schemas: A dictionary mapping the schema name to the mashmallow
                    schema
    :param endpoint: The name of the endpoint to register in flask
    :param rule: The url routing rule for the endpoint
    """

    schemas = {}
    endpoint = None
    rule = '/'
    temp_env = jinja2.Environment(
        loader=jinja2.PackageLoader('dataservice.api', 'templates')
    )

    def __init__(self, *args, **kwargs):
        super(CRUDView, self).__init__(*args, **kwargs)

    @classmethod
    def register_spec(cls, spec):
        """
        Register the schemas and their common formats for all subclasses

        :param spec: the :class:`~apispec.APISpec` to register schemas and
            views on
        """
        for c in cls.__subclasses__():
            if len(c.schemas) == 0:
                continue

            for name, schema in c.schemas.items():
                # Entity response schemas
                spec.definition(name, schema=schema)
                ResponseSchema = response_generator(schema)
                spec.definition(name + 'Response', schema=ResponseSchema)

                # Pagination schemas
                if c.__name__.endswith('ListAPI'):
                    url = c.rule
                    PaginatedSchema = paginated_generator(url, schema)
                    spec.definition(name + 'Paginated', schema=PaginatedSchema)

        # Error response schemas
        not_found_schema_cls = error_response_generator(404)
        spec.definition('NotFoundErrorResponse',
                        schema=not_found_schema_cls)
        client_error_schema_cls = error_response_generator(400)
        spec.definition('ClientErrorResponse',
                        schema=client_error_schema_cls)

    @staticmethod
    def register_views(app):
        """
        Registers views for each subclass on the app or blueprint

        :param app: the application or blueprint to register the views on
        """
        views = []
        for c in CRUDView.__subclasses__():
            # Do not register the view if there was no endpoint defined
            if c.endpoint is None:
                continue
            methods = c.methods

            for meth in c.methods:

                if hasattr(c, meth.lower()):
                    CRUDView._format_docstring(getattr(c, meth.lower()))

            view = c.as_view(c.endpoint)
            app.add_url_rule(c.rule, view_func=view, methods=methods)
            views.append(view)
        return views

    @staticmethod
    def _format_docstring(func):
        """
        Formats a doc string by parsing the yaml below the '---' line in a
        function's doc string.
        """
        yaml_start = func.__doc__.find('---')
        # No yaml section
        if yaml_start == -1:
            return
        yaml_spec = yaml.safe_load(func.__doc__[yaml_start + 3:])

        # No template to insert
        if 'template' not in yaml_spec:
            return

        templated_spec = CRUDView._load_template(yaml_spec['template'])
        if not templated_spec:
            return

        # Remove the template tree and update with loaded template
        del yaml_spec['template']
        templated_spec.update(yaml_spec)

        # Dump the deserialized spec back to yaml in the docstring
        func.__doc__ = func.__doc__[:yaml_start + 4]
        func.__doc__ += yaml.dump(templated_spec, default_flow_style=False)
        # The docstring is now ready for further processing by apispec

    @staticmethod
    def _load_template(template):
        """
        Renders a yaml template from a given path with optional properties

        Given a :param:`template`:

            {
              'path': 'my_template.yml',
              'properties': {'name': 'My Field'}
            }

        A yaml template, `my_template.yml`:

            properties:
              name:
                {{ name }}

        Will be loaded as:

            {
              'properties': {
                'name': 'My Field'
              }
            }


        :param template: A dict that must have a `path` key with the path to
                         find the template at and optional `properties`
                         that will be used to fill in the template.

        :retruns: A dict from the templated yaml file
        """
        if 'path' not in template:
            raise ValueError('Expected a path for the template')
        properties = template.get('properties', {})
        temp = CRUDView._render_template(template['path'], **properties)
        return temp

    def _render_template(template_name, **props):
        """
        Renders a yaml file templated with jinja2 and deserializes to a dict
        """
        template = CRUDView.temp_env.get_template(template_name)
        return yaml.safe_load(template.render(**props))

    @classmethod
    def endpoints(cls):
        """
        Returns endpoints for all subclasses
        """
        return [c.endpoint for c in cls.__subclasses__()]

    def dispatch_request(self, *args, **kwargs):
        """
        Override MethodView's dispatch_request method to execute additional
        needed functionality for every CRUD request:

            - Sends request as an event to sns

            - Execute each request with sqlalchemy autoflush turned off.
              This prevents the model event listeners from triggering
              inadvertently. It happens when the db session goes out of scope
              and when Marshmallow loads an object into the session and does a
              merge during a patch request. Its better to explicitly flush
              the session.
        """
        # Autoflush off
        db.session.autoflush = False

        # Send request
        resp = super(CRUDView, self).dispatch_request(*args, **kwargs)

        if isinstance(resp, tuple):
            status = resp[1]
            resp = resp[0]
        else:
            status = resp.status_code

        # Send event to sns
        self.send_sns(resp)

        # Autoflush back on
        db.session.autoflush = True

        return resp, status

    def send_sns(self, resp):
        """
        Send an event to SNS containing the response if:
        - There is a topic ARN in the config
        - Response is 2xx
        - Method is POST, PATCH, PUT, or DELETE
        """
        # Bail if there is no ARN in the config
        if ('SNS_EVENT_ARN' not in current_app.config or
                current_app.config['SNS_EVENT_ARN'] is None):
            return
        arn = current_app.config['SNS_EVENT_ARN']

        # Bail early if not a good response
        if resp.status_code >= 300:
            return

        # Bail early if not an interesting method type
        meth = request.method.lower()
        if meth not in ['post', 'patch', 'put', 'delete']:
            return

        message = {'default': json.dumps({
            'path': request.path,
            'method': meth,
            'api_version': current_app.config['PKG_VERSION'],
            'api_commit': current_app.config['GIT_COMMIT'],
            'data': json.loads(resp.data.decode('utf8'))
        })}

        client = boto3.client('sns', region_name='us-east-1')
        client.publish(TopicArn=arn,
                       MessageStructure='json',
                       Message=json.dumps(message))
