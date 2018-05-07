from flask import abort, request
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.family_relationship.schemas import (
    FamilyRelationshipSchema
)
from dataservice.api.common.views import CRUDView


class FamilyRelationshipListAPI(CRUDView):
    """
    FamilyRelationship REST API
    """
    endpoint = 'family_relationships_list'
    rule = '/family-relationships'
    schemas = {'FamilyRelationship': FamilyRelationshipSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all family_relationships
        ---
        description: Get all family_relationships
        template:
          path:
            get_list.yml
          properties:
            resource:
              FamilyRelationship
        """
        q = FamilyRelationship.query

        # Filter by study
        from dataservice.api.participant.models import Participant
        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(FamilyRelationship.participant)
                 .filter(Participant.study_id == study_id))

        return (FamilyRelationshipSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new family_relationship
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              FamilyRelationship
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            fr = FamilyRelationshipSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create family_relationship: {}'
                  .format(e.messages))

        # Add to and save in database
        db.session.add(fr)
        db.session.commit()

        return FamilyRelationshipSchema(201, 'family_relationship {} created'
                                        .format(fr.kf_id)).jsonify(fr), 201


class FamilyRelationshipAPI(CRUDView):
    """
    FamilyRelationship REST API
    """
    endpoint = 'family_relationships'
    rule = '/family-relationships/<string:kf_id>'
    schemas = {'FamilyRelationship': FamilyRelationshipSchema}

    def get(self, kf_id):
        """
        Get a family_relationship by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              FamilyRelationship
        """
        # Get one
        fr = FamilyRelationship.query.get(kf_id)
        if fr is None:
            abort(404, 'could not find {} `{}`'
                  .format('family_relationship', kf_id))
        return FamilyRelationshipSchema().jsonify(fr)

    def patch(self, kf_id):
        """
        Update an existing family_relationship.

        Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              FamilyRelationship
        """
        fr = FamilyRelationship.query.get(kf_id)
        if fr is None:
            abort(404, 'could not find {} `{}`'
                  .format('family_relationship', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            fr = FamilyRelationshipSchema(strict=True).load(body, instance=fr,
                                                            partial=True).data
        except ValidationError as err:
            abort(400, 'could not update family_relationship: {}'
                  .format(err.messages))

        db.session.add(fr)
        db.session.commit()

        return FamilyRelationshipSchema(
            200, 'family_relationship {} updated'.format(fr.kf_id)
        ).jsonify(fr), 200

    def delete(self, kf_id):
        """
        Delete family_relationship by id

        Deletes a family_relationship given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              FamilyRelationship
        """

        # Check if family_relationship exists
        fr = FamilyRelationship.query.get(kf_id)
        if fr is None:
            abort(404, 'could not find {} `{}`'
                  .format('family_relationship', kf_id))

        # Save in database
        db.session.delete(fr)
        db.session.commit()

        return FamilyRelationshipSchema(200, 'family_relationship {} deleted'
                                        .format(fr.kf_id)).jsonify(fr), 200
