from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.sample_relationship.models import SampleRelationship
from dataservice.api.sample_relationship.schemas import (
    SampleRelationshipSchema,
    SampleRelationshipFilterSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class SampleRelationshipListAPI(CRUDView):
    """
    SampleRelationship REST API
    """
    endpoint = 'sample_relationships_list'
    rule = '/sample-relationships'
    schemas = {'SampleRelationship': SampleRelationshipSchema}

    @paginated
    @use_args(filter_schema_factory(SampleRelationshipFilterSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get all sample_relationships
        ---
        description: Get all sample_relationships
        template:
          path:
            get_list.yml
          properties:
            resource:
              SampleRelationship
        """
        # Get and remove special filter parameters - those which are not
        # part of model properties
        # Study id
        study_id = filter_params.pop('study_id', None)
        # Sample id
        sample_id = filter_params.pop('sample_id', None)

        # Get sample relationships joined w samples
        q = SampleRelationship.query_all_relationships(
            sample_kf_id=sample_id,
            model_filter_params=filter_params)

        # Filter by study
        if study_id:
            from dataservice.api.participant.models import Participant
            q = (q.join(Participant.samples)
                 .filter(Participant.study_id == study_id))

        return (SampleRelationshipSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new sample_relationship
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              SampleRelationship
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            sa = SampleRelationshipSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create sample_relationship: {}'
                  .format(e.messages))

        # Add to and save in database
        db.session.add(sa)
        db.session.commit()

        return SampleRelationshipSchema(201, 'sample_relationship {} created'
                                        .format(sa.kf_id)).jsonify(sa), 201


class SampleRelationshipAPI(CRUDView):
    """
    SampleRelationship REST API
    """
    endpoint = 'sample_relationships'
    rule = '/sample-relationships/<string:kf_id>'
    schemas = {'SampleRelationship': SampleRelationshipSchema}

    def get(self, kf_id):
        """
        Get a sample_relationship by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              SampleRelationship
        """
        # Get one
        sa = SampleRelationship.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('sample_relationship', kf_id))
        return SampleRelationshipSchema().jsonify(sa)

    def patch(self, kf_id):
        """
        Update an existing sample_relationship.

        Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              SampleRelationship
        """
        sa = SampleRelationship.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('sample_relationship', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            sa = SampleRelationshipSchema(strict=True).load(body, instance=sa,
                                                            partial=True).data
        except ValidationError as err:
            abort(400, 'could not update sample_relationship: {}'
                  .format(err.messages))

        db.session.add(sa)
        db.session.commit()

        return SampleRelationshipSchema(
            200, 'sample_relationship {} updated'.format(sa.kf_id)
        ).jsonify(sa), 200

    def delete(self, kf_id):
        """
        Delete sample_relationship by id

        Deletes a sample_relationship given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              SampleRelationship
        """

        # Check if sample_relationship exists
        sa = SampleRelationship.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('sample_relationship', kf_id))

        # Save in database
        db.session.delete(sa)
        db.session.commit()

        return SampleRelationshipSchema(200, 'sample_relationship {} deleted'
                                        .format(sa.kf_id)).jsonify(sa), 200
