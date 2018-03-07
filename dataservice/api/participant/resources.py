from pprint import pprint
from flask import abort, request
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.participant.models import Participant
from dataservice.api.participant.schemas import ParticipantSchema
from dataservice.api.common.views import CRUDView


class ParticipantListAPI(CRUDView):
    """
    Participant API
    """
    endpoint = 'participants_list'
    rule = '/participants'
    schemas = {'Participant': ParticipantSchema}

    @paginated
    def get(self, after, limit):
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
        q = (Participant.query
                        .options(joinedload(Participant.diagnoses))
                        .options(joinedload(Participant.samples))
                        .options(joinedload(Participant.phenotypes))
                        .options(joinedload(Participant.demographic))
                        .options(joinedload(Participant.outcomes)))

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
        try:
            p = ParticipantSchema(strict=True).load(request.json).data
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
        try:
            participant = Participant.query.filter_by(kf_id=kf_id).one()
        except NoResultFound:
            abort(404, 'could not find {} `{}`'
                  .format('Participant', kf_id))
        return ParticipantSchema().jsonify(participant)

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
        body = request.json or {}
        try:
            p = Participant.query.filter_by(kf_id=kf_id).one()
        except NoResultFound:
            abort(404, 'could not find {} `{}`'
                  .format('Participant', kf_id))

        # Partial update - validate but allow missing required fields
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
        try:
            p = Participant.query.filter_by(kf_id=kf_id).one()
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('Participant', kf_id))

        db.session.delete(p)
        db.session.commit()

        return ParticipantSchema(
            200, 'participant {} deleted'.format(p.kf_id)
        ).jsonify(p), 200
