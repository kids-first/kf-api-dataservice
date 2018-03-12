from flask import abort, request
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.demographic.models import Demographic
from dataservice.api.demographic.schemas import DemographicSchema
from dataservice.api.common.views import CRUDView


class DemographicListAPI(CRUDView):
    """
    Demographic REST API
    """
    endpoint = 'demographics_list'
    rule = '/demographics'
    schemas = {'Demographic': DemographicSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all demographics
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              Demographic
        """
        q = Demographic.query
        return (DemographicSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new demographic
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Demographic
        """

        body = request.json

        # Deserialize
        try:
            d = DemographicSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create demographic: {}'.format(e.messages))

        db.session.add(d)
        db.session.commit()

        return DemographicSchema(201, 'demographic {} created'
                                 .format(d.kf_id)).jsonify(d), 201


class DemographicAPI(CRUDView):
    """
    Demographic REST API
    """
    endpoint = 'demographics'
    rule = '/demographics/<string:kf_id>'
    schemas = {'Demographic': DemographicSchema}

    def get(self, kf_id):
        """
        Get a demographic by id

        Get a demographic by Kids First id or get all demographics if
        Kids First id is None
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Demographic
        """
        # Get all
        if kf_id is None:
            dm = Demographic.query.all()
            return DemographicSchema(many=True).jsonify(dm)
        # Get one
        else:
            dm = Demographic.query.get(kf_id)
            if dm is None:
                abort(404, 'could not find {} `{}`'
                      .format('demographic', kf_id))
            return DemographicSchema().jsonify(dm)

    def patch(self, kf_id):
        """
        Update an existing demographic. Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Demographic
        """
        dm = Demographic.query.get(kf_id)
        if dm is None:
            abort(404, 'could not find {} `{}`'
                  .format('demographic', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.json or {}
        try:
            dm = DemographicSchema(strict=True).load(body, instance=dm,
                                                     partial=True).data
        except ValidationError as err:
            abort(400, 'could not update demographic: {}'.format(err.messages))

        db.session.add(dm)
        db.session.commit()

        return DemographicSchema(
            200, 'demographic {} updated'.format(dm.kf_id)
        ).jsonify(dm), 200

    def delete(self, kf_id):
        """
        Delete demographic by id

        Deletes a demographic given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Demographic
        """
        # Check if demographic exists
        dm = Demographic.query.get(kf_id)
        if dm is None:
            abort(404, 'could not find {} `{}`'
                  .format('demographic', kf_id))

        # Save in database
        db.session.delete(dm)
        db.session.commit()

        return DemographicSchema(200, 'demographic {} deleted'
                                 .format(dm.kf_id)).jsonify(dm), 200
