from flask import abort, request
from sqlalchemy.orm import joinedload
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.participant.models import Participant
from dataservice.api.participant.schemas import (
    ParticipantSchema,
    ParticipantFilterSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class ParticipantListAPI(CRUDView):
    """
    Participant API
    """
    endpoint = 'participants_list'
    rule = '/participants'
    schemas = {'Participant': ParticipantSchema}

    @paginated
    @use_args(filter_schema_factory(ParticipantFilterSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get a paginated participants
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              Participant
        """
        # Apply entity filter params
        q = (Participant.query.filter_by(**filter_params)
                        .options(joinedload(Participant.diagnoses)
                                 .load_only('kf_id'))
                        .options(joinedload(Participant.biospecimens)
                                 .load_only('kf_id'))
                        .options(joinedload(Participant.phenotypes)
                                 .load_only('kf_id'))
                        .options(joinedload(Participant.outcomes)
                                 .load_only('kf_id')))

        return (ParticipantSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new participant
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Participant
        """
        body = request.get_json(force=True)
        try:
            p = ParticipantSchema(strict=True).load(body).data
        except ValidationError as err:
            abort(400, 'could not create participant: {}'.format(err.messages))

        db.session.add(p)
        db.session.commit()
        return ParticipantSchema(
            201, 'participant {} created'.format(p.kf_id)
        ).jsonify(p), 201


class ParticipantAPI(CRUDView):
    """
    Participant API
    """
    endpoint = 'participants'
    rule = '/participants/<string:kf_id>'
    schemas = {'Participant': ParticipantSchema}

    def get(self, kf_id):
        """
        Get a participant by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Participant
        """
        p = Participant.query.get(kf_id)
        if p is None:
            abort(404, 'could not find {} `{}`'
                  .format('participant', kf_id))

        return ParticipantSchema().jsonify(p)

    def patch(self, kf_id):
        """
        Update an existing participant. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Participant
        """
        p = Participant.query.get(kf_id)
        if p is None:
            abort(404, 'could not find {} `{}`'
                  .format('participant', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            p = ParticipantSchema(strict=True).load(body, instance=p,
                                                    partial=True).data
        except ValidationError as err:
            abort(400, 'could not update participant: {}'.format(err.messages))

        db.session.add(p)
        db.session.commit()

        return ParticipantSchema(
            200, 'participant {} updated'.format(p.kf_id)
        ).jsonify(p), 200

    def delete(self, kf_id):
        """
        Delete participant by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Participant
        """
        p = Participant.query.get(kf_id)
        if p is None:
            abort(404, 'could not find {} `{}`'
                  .format('participant', kf_id))

        db.session.delete(p)
        db.session.commit()

        return ParticipantSchema(
            200, 'participant {} deleted'.format(p.kf_id)
        ).jsonify(p), 200
