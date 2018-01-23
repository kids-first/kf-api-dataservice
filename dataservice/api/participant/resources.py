from flask import abort, request
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.participant.schemas import ParticipantSchema 


class ParticipantAPI(MethodView):
    def get(self, kf_id):
        """
        Get a participant by id

        Gets a participant given a Kids First id
        """
        if kf_id is None:
            return (ParticipantSchema(many=True)
                    .jsonify(Participant.query.all()))
        else:
            try:
                participant = Participant.query.filter_by(kf_id=kf_id).one()
            except NoResultFound:
                abort(404, 'could not find {} `{}`'
                      .format('Participant', kf_id))
            return ParticipantSchema().jsonify(participant)

    def post(self):
        """
        Create a new participant
        """
        body = request.json
        p = Participant(external_id=body.get('external_id'))
        db.session.add(p)
        db.session.commit()

        return ParticipantSchema(
                201, 'participant {} created'.format(p.kf_id)
               ).jsonify(p), 201

    def put(self, kf_id):
        """
        Update an existing participant
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

        Deletes a participant given a Kids First id
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
