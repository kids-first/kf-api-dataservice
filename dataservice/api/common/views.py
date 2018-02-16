import yaml
import jinja2
from flask.views import MethodView
from flask import render_template
from dataservice.api.common.schemas import (
    response_generator,
    paginated_generator
)


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
                spec.definition(name, schema=schema)
                ResponseSchema = response_generator(schema)
                spec.definition(name+'Response', schema=ResponseSchema)
                PaginatedSchema = paginated_generator(schema)
                spec.definition(name+'Paginated', schema=PaginatedSchema)

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
        yaml_spec = yaml.safe_load(func.__doc__[yaml_start+3:])

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
        func.__doc__ = func.__doc__[:yaml_start+4]
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
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('dataservice.api', 'templates')
        )
        template = env.get_template(template_name)
        return yaml.safe_load(template.render(**props))

    @classmethod
    def endpoints(cls):
        """
        Returns endpoints for all subclasses
        """
        return [c.endpoint for c in cls.__subclasses__()]