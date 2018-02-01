from flask import (
    abort,
    request
)
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.errors import handle_integrity_error
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.diagnosis.schemas import DiagnosisSchema


class DiagnosisAPI(MethodView):
    """
    Diagnosis REST API
    """

    def get(self, kf_id):
        """
        Get a diagnosis by id or get all diagnoses

        Get a diagnosis by Kids First id or get all diagnoses if
        Kids First id is None
        """
        # Get all
        if kf_id is None:
            d = Diagnosis.query.all()
            return DiagnosisSchema(many=True).jsonify(d)
        # Get one
        else:
            try:
                d = Diagnosis.query.filter_by(kf_id=kf_id).one()
            # Not found in database
            except NoResultFound:
                abort(404, 'could not find {} `{}`'
                      .format('diagnosis', kf_id))
            return DiagnosisSchema().jsonify(d)

    def post(self):
        """
        Create a new diagnosis
        """

        body = request.json

        # Deserialize
        try:
            d = DiagnosisSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create diagnosis: {}'.format(e.messages))

        # Add to and save in database
        try:
            db.session.add(d)
            db.session.commit()
        # Database error
        except IntegrityError as e:
            db.session.rollback()
            context = {'method': 'create', 'entity': 'diagnosis',
                       'ref_entity': 'participant', 'exception': e}
            abort(400, handle_integrity_error(**context))

        return DiagnosisSchema(201, 'diagnosis {} created'
                               .format(d.kf_id)).jsonify(d), 201

    def put(self, kf_id):
        """
        Update existing diagnosis

        Update an existing diagnosis given a Kids First id
        """
        body = request.json
        try:
            # Check if diagnosis exists
            d1 = Diagnosis.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('diagnosis', kf_id))

        # Validation only
        try:
            d = DiagnosisSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not update diagnosis: {}'.format(e.messages))

        # Deserialize
        d1.external_id = body.get('external_id')
        d1.diagnosis = body.get('diagnosis')
        d1.age_at_event_days = body.get('age_at_event_days')
        d1.participant_id = body.get('participant_id')

        # Save to database
        try:
            db.session.commit()
        # Database error
        except IntegrityError as e:
            db.session.rollback()
            context = {'method': 'update', 'entity': 'diagnosis',
                       'ref_entity': 'participant', 'exception': e}
            abort(400, handle_integrity_error(**context))

        return DiagnosisSchema(200, 'diagnosis {} updated'
                               .format(d1.kf_id)).jsonify(d1), 200

    def delete(self, kf_id):
        """
        Delete diagnosis by id

        Deletes a diagnosis given a Kids First id
        """

        # Check if diagnosis exists
        try:
            d = Diagnosis.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('diagnosis', kf_id))

        # Save in database
        db.session.delete(d)
        db.session.commit()

        return DiagnosisSchema(200, 'diagnosis {} deleted'
                               .format(d.kf_id)).jsonify(d), 200
