from flask import abort, request
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.aliquot.schemas import AliquotSchema
from dataservice.api.common.views import CRUDView


class AliquotListAPI(CRUDView):
    """
    Aliquot REST API
    """
    endpoint = 'aliquots_list'
    rule = '/aliquots'
    schemas = {'Aliquot': AliquotSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all aliquots
        ---
        description: Get all aliquots
        template:
          path:
            get_list.yml
          properties:
            resource:
              Aliquot
        """
        q = Aliquot.query

        return (AliquotSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new aliquot
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Aliquot
        """

        body = request.json

        # Deserialize
        try:
            al = AliquotSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create aliquot: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(al)
        db.session.commit()

        return AliquotSchema(201, 'aliquot {} created'
                             .format(al.kf_id)).jsonify(al), 201


class AliquotAPI(CRUDView):
    """
    Aliquot REST API
    """
    endpoint = 'aliquots'
    rule = '/aliquots/<string:kf_id>'
    schemas = {'Aliquot': AliquotSchema}

    def get(self, kf_id):
        """
        Get a aliquot by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Aliquot
        """
        # Get one
        al = Aliquot.query.get(kf_id)
        if al is None:
            abort(404, 'could not find {} `{}`'
                  .format('aliquot', kf_id))
        return AliquotSchema().jsonify(al)

    def patch(self, kf_id):
        """
        Update an existing aliquot. Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Aliquot
        """
        al = Aliquot.query.get(kf_id)
        if al is None:
            abort(404, 'could not find {} `{}`'
                  .format('aliquot', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.json or {}
        try:
            al = AliquotSchema(strict=True).load(body, instance=al,
                                                 partial=True).data
        except ValidationError as err:
            abort(400, 'could not update aliquot: {}'.format(err.messages))

        db.session.add(al)
        db.session.commit()

        return AliquotSchema(
            200, 'aliquot {} updated'.format(al.kf_id)
        ).jsonify(al), 200

    def delete(self, kf_id):
        """
        Delete aliquot by id

        Deletes a aliquot given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Aliquot
        """

        # Check if aliquot exists
        al = Aliquot.query.get(kf_id)
        if al is None:
            abort(404, 'could not find {} `{}`'
                  .format('aliquot', kf_id))

        # Save in database
        db.session.delete(al)
        db.session.commit()

        return AliquotSchema(200, 'aliquot {} deleted'
                             .format(al.kf_id)).jsonify(al), 200
