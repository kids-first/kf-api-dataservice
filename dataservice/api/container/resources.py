from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.container.models import (
    Container,
)
from dataservice.api.container.schemas import (
    ContainerSchema,
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class ContainerListAPI(CRUDView):
    """
    Container REST API
    """
    endpoint = 'containers_list'
    rule = '/containers'
    schemas = {'Container': ContainerSchema}

    @paginated
    @use_args(filter_schema_factory(ContainerSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get all containers
        ---
        description: Get all containers
        template:
          path:
            get_list.yml
          properties:
            resource:
              Container
        """
        # Get and remove special filter params that are not attributes of model
        study_id = filter_params.pop('study_id', None)

        # Apply filter params
        q = (Container.query
             .filter_by(**filter_params))

        # Apply study_id filter and diagnosis_id filter
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen

        if study_id:
            q = (q.join(Container.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id))

        return (ContainerSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new container
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Container
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            s = ContainerSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create container: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(s)
        db.session.commit()

        return ContainerSchema(201, 'container {} created'
                               .format(s.kf_id)).jsonify(s), 201


class ContainerAPI(CRUDView):
    """
    Container REST API
    """
    endpoint = 'containers'
    rule = '/containers/<string:kf_id>'
    schemas = {'Container': ContainerSchema}

    def get(self, kf_id):
        """
        Get containers by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Container
        """
        sa = Container.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('container', kf_id))
        return ContainerSchema().jsonify(sa)

    def patch(self, kf_id):
        """
        Update an existing container. Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Container
        """
        sa = Container.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('container', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            sa = ContainerSchema(strict=True).load(body, instance=sa,
                                                   partial=True).data
        except ValidationError as err:
            abort(400, 'could not update container: {}'.format(err.messages))

        db.session.add(sa)
        db.session.commit()

        return ContainerSchema(
            200, 'container {} updated'.format(sa.kf_id)
        ).jsonify(sa), 200

    def delete(self, kf_id):
        """
        Delete container by id

        Deletes a container given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Container
        """

        # Check if container exists
        sa = Container.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('container', kf_id))

        # Save in database
        db.session.delete(sa)
        db.session.commit()

        return ContainerSchema(200, 'container {} deleted'
                               .format(sa.kf_id)).jsonify(sa), 200
