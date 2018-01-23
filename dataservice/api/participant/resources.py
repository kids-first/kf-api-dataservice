from flask import abort, request, Blueprint
from flask.views import MethodView

from dataservice.extensions import db
from dataservice.api.participant.models import Participant

participant_api = Blueprint('participant', __name__)

class ParticipantAPI(MethodView):
    def get(self, kf_id):
        """
        Get a participant by id
        Gets a participant given a Kids First id
        """
        if kf_id is None:
            return Participant.query.all()
        else:
            participant = Participant.query.filter_by(kf_id=kf_id).\
                one_or_none()
            return participant

    def post(self, kf_id):
        """
        Update an existing participant
        """
        body = request.json
        participant = Participant.query.filter_by(kf_id=kf_id).one_or_none()

        if not participant:
            self._not_found(kf_id)

        participant.external_id = body.get('external_id')
        db.session.commit()

        return participant, 201

    def put(self, kf_id):
        """
        Update an existing participant
        """
        body = request.json
        participant = Participant.query.filter_by(kf_id=kf_id).one_or_none()

        if not participant:
            self._not_found(kf_id)

        participant.external_id = body.get('external_id')
        db.session.commit()

        return participant, 201

    def delete(self, kf_id):
        """
        Delete participant by id

        Deletes a participant given a Kids First id
        """
        participant = Participant.query.filter_by(kf_id=kf_id).one_or_none()

        if not participant:
            abort(404)

        db.session.delete(participant)
        db.session.commit()

        return participant
