from flask import abort, request
from marshmallow import ValidationError

from dataservice.extensions import cache, db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.sample.models import Sample
from dataservice.api.sample.schemas import SampleSchema
from dataservice.api.common.views import CRUDView


class SampleListAPI(CRUDView):
    """
    Sample REST API
    """
    endpoint = 'samples_list'
    rule = '/samples'
    schemas = {'Sample': SampleSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all samples
        ---
        description: Get all samples
        template:
          path:
            get_list.yml
          properties:
            resource:
              Sample
        """
        q = Sample.query

        return (SampleSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new sample
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Sample
        """

        body = request.json

        # Deserialize
        try:
            s = SampleSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create sample: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(s)
        db.session.commit()

        return SampleSchema(201, 'sample {} created'
                            .format(s.kf_id)).jsonify(s), 201


class SampleAPI(CRUDView):
    """
    Sample REST API
    """
    endpoint = 'samples'
    rule = '/samples/<string:kf_id>'
    schemas = {'Sample': SampleSchema}

    def get(self, kf_id):
        """
        Get samples by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Sample
        """
        sa = Sample.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('sample', kf_id))
        return SampleSchema().jsonify(sa)

    def patch(self, kf_id):
        """
        Update an existing sample. Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Sample
        """
        sa = Sample.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('sample', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.json or {}
        try:
            sa = SampleSchema(strict=True).load(body, instance=sa,
                                                partial=True).data
        except ValidationError as err:
            abort(400, 'could not update sample: {}'.format(err.messages))

        db.session.add(sa)
        db.session.commit()

        return SampleSchema(
            200, 'sample {} updated'.format(sa.kf_id)
        ).jsonify(sa), 200

    def delete(self, kf_id):
        """
        Delete sample by id

        Deletes a sample given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Sample
        """

        # Check if sample exists
        sa = Sample.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('sample', kf_id))

        # Save in database
        db.session.delete(sa)
        db.session.commit()

        return SampleSchema(200, 'sample {} deleted'
                            .format(sa.kf_id)).jsonify(sa), 200
