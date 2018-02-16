from flask import abort, request
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from dataservice.extensions import db
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

    def get(self):
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
        return (ParticipantSchema(many=True)
                .jsonify(Participant.query.all()))

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

    def put(self, kf_id):
        """
        Update an existing participant
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Participant
        """
        body = request.json
        try:
            p = Participant.query.filter_by(kf_id=kf_id).one()
        except NoResultFound:
            abort(404, 'could not find {} `{}`'
                  .format('Participant', kf_id))

        p.external_id = body.get('external_id')
        p.study_id = body.get('study_id')
        db.session.commit()

        return ParticipantSchema(
            201, 'participant {} updated'.format(p.kf_id)
        ).jsonify(p), 201

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
