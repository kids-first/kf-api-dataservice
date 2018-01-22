from flask import request
from flask_restplus import Namespace, Resource

from dataservice.extensions import db
from dataservice.api.participant import models
from dataservice.api.common.formatters import kf_response

description = open('dataservice/api/participant/README.md').read()

participant_api = Namespace(name='participants', description=description)

from dataservice.api.participant.serializers import (  # noqa
    participant_fields,
    participant_list,
    participant_response
)


@participant_api.route('/')
class ParticipantList(Resource):
    @participant_api.marshal_with(participant_list)
    def get(self):
        """
        Get all participants

        Returns paginated participants
        """
        participants = models.Participant.query.all()
        return kf_response(participants, 200, '{} participants'.
                           format(len(participants)))

    @participant_api.marshal_with(participant_response)
    @participant_api.doc(responses={201: 'participant created',
                                    400: 'invalid data'})
    @participant_api.expect(participant_fields)
    def post(self):
        """
        Create a new participant

        Creates a new participant and assigns a Kids First id
        """
        body = request.json
        participant = models.Participant(**body)
        db.session.add(participant)
        db.session.commit()

        return kf_response(participant, 201, 'participant created')


@participant_api.route('/<string:kf_id>')
class Participant(Resource):
    @participant_api.marshal_with(participant_response)
    @participant_api.doc(responses={200: 'participant found',
                                    404: 'participant not found'})
    def get(self, kf_id):
        """
        Get a participant by id
        Gets a participant given a Kids First id
        """
        participant = models.Participant.query.filter_by(kf_id=kf_id).\
            one_or_none()
        if not participant:
            return self._not_found(kf_id)

        return kf_response(participant, 200, 'participant found')

    @participant_api.marshal_with(participant_response)
    @participant_api.doc(responses={201: 'participant updated',
                                    400: 'invalid data',
                                    404: 'participant not found'})
    @participant_api.expect(participant_fields)
    def put(self, kf_id):
        """
        Update an existing participant
        """
        body = request.json
        participant = models.Participant.query.\
            filter_by(kf_id=kf_id).one_or_none()

        if not participant:
            self._not_found(kf_id)

        participant.external_id = body.get('external_id')
        db.session.commit()

        return kf_response(participant, 201, 'participant updated')

    @participant_api.marshal_with(participant_response)
    @participant_api.doc(responses={204: 'participant deleted',
                                    404: 'participant not found'})
    def delete(self, kf_id):
        """
        Delete participant by id

        Deletes a participant given a Kids First id
        """
        participant = models.Participant.query.\
            filter_by(kf_id=kf_id).one_or_none()

        if not participant:
            self._not_found(kf_id)

        db.session.delete(participant)
        db.session.commit()

        return kf_response(participant, 200, 'participant deleted')

    def _not_found(self, kf_id):
        """
        Temporary helper - will do error handling better later
        """
        message = 'participant with kf_id \'{}\' not found'.format(kf_id)
        return kf_response(code=404,
                           message=message)
