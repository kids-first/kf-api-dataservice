from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import Load, load_only

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.outcome.models import Outcome
from dataservice.api.outcome.schemas import OutcomeSchema
from dataservice.api.common.views import CRUDView


class OutcomeListAPI(CRUDView):
    """
    Outcome REST API
    """
    endpoint = 'outcomes_list'
    rule = '/outcomes'
    schemas = {'Outcome': OutcomeSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all outcomes
        ---
        description: Get all outcomes
        template:
          path:
            get_list.yml
          properties:
            resource:
              Outcome
        """
        q = Outcome.query

        # Filter by study
        from dataservice.api.participant.models import Participant
        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(Participant.outcomes)
                 .filter(Participant.study_id == study_id))

        return (OutcomeSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new outcome
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Outcome
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            o = OutcomeSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create outcome: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(o)
        db.session.commit()

        return OutcomeSchema(201, 'outcome {} created'
                             .format(o.kf_id)).jsonify(o), 201


class OutcomeAPI(CRUDView):
    """
    Outcome REST API
    """
    endpoint = 'outcomes'
    rule = '/outcomes/<string:kf_id>'
    schemas = {'Outcome': OutcomeSchema}

    def get(self, kf_id):
        """
        Get a outcome by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Outcome
        """
        # Get one
        o = Outcome.query.get(kf_id)
        # Not found in database
        if o is None:
            abort(404, 'could not find {} `{}`'
                  .format('outcome', kf_id))
        return OutcomeSchema().jsonify(o)

    def patch(self, kf_id):
        """
        Update an existing outcome

        Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Outcome
        """
        # Check if outcome exists
        o = Outcome.query.get(kf_id)
        # Not found in database
        if o is None:
            abort(404, 'could not find {} `{}`'.format('outcome', kf_id))
        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        # Validation only
        try:
            o = OutcomeSchema(strict=True).load(body, instance=o,
                                                partial=True).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not update outcome: {}'.format(e.messages))

        # Save to database
        db.session.add(o)
        db.session.commit()

        return OutcomeSchema(200, 'outcome {} updated'
                             .format(o.kf_id)).jsonify(o), 200

    def delete(self, kf_id):
        """
        Delete outcome by id

        Deletes a outcome given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Outcome
        """

        # Check if outcome exists
        o = Outcome.query.get(kf_id)
        # Not found in database
        if o is None:
            abort(404, 'could not find {} `{}`'.format('outcome', kf_id))

        # Save in database
        db.session.delete(o)
        db.session.commit()

        return OutcomeSchema(200, 'outcome {} deleted'
                             .format(o.kf_id)).jsonify(o), 200
