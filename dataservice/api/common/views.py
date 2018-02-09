from flask.views import MethodView
from dataservice.api.common.schemas import (
    response_generator,
    paginated_generator
)

http_method_funcs = frozenset(['get', 'post', 'head', 'options',
                               'delete', 'put', 'trace', 'patch'])


class CRUDView(MethodView):
    """
    Extends :class:`~flask.views.MethodView` with class attributes needed
    to properly register mashmallow schemas and url rules on the apispec
    swagger generator.

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
            view = c.as_view(c.endpoint)
            app.add_url_rule(c.rule, view_func=view, methods=methods)
            views.append(view)
        return views

    @classmethod
    def endpoints(cls):
        """
        Returns endpoints for all subclasses
        """
        return [c.endpoint for c in cls.__subclasses__()]
