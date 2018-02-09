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
        description: Get participants
        tags:
        - Participant
        responses:
          200:
            description: Particpants found
            schema:
              $ref: '#/definitions/ParticipantPaginated'
        """
        return (ParticipantSchema(many=True)
                .jsonify(Participant.query.all()))

    def post(self):
        """
        Create a new participant
        ---
        description: Create a new particpant
        tags:
        - Participant
        parameters:
        - name: body
          in: body
          description: Content
          required: true
          schema:
            $ref: "#/definitions/Participant"
        responses:
          200:
            description: Participant created
            schema:
              $ref: '#/definitions/ParticipantResponse'
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
        description: Get participant by id
        tags:
        - Participant
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of person to return"
          required: true
          type: "string"
        responses:
          200:
            description: Particpant found
            schema:
              $ref: '#/definitions/ParticipantResponse'
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
        description: Update a particpant
        tags:
        - Participant
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of person to return"
          required: true
          type: "string"
        - name: "body"
          in: "body"
          description: "Person source identifier"
          required: true
          schema:
            $ref: "#/definitions/Participant"
        responses:
          200:
            description: Participant updated
            schema:
              $ref: '#/definitions/ParticipantResponse'
        """
        body = request.json
        try:
            p = Participant.query.filter_by(kf_id=kf_id).one()
        except NoResultFound:
            abort(404, 'could not find {} `{}`'
                  .format('Participant', kf_id))

        p.external_id = body.get('external_id')
        db.session.commit()

        return ParticipantSchema(
            201, 'participant {} updated'.format(p.kf_id)
        ).jsonify(p), 201

    def delete(self, kf_id):
        """
        Delete participant by id
        ---
        description: Delete a participant
        tags:
        - Participant
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of person to return"
          required: true
          type: "string"
        responses:
          200:
            description: Participant deleted
            schema:
              $ref: '#/definitions/ParticipantResponse'
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
