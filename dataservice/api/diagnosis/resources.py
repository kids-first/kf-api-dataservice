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
        try:
            # Deserialize
            d = DiagnosisSchema(strict=True).load(body).data
            # Add to and save in database
            db.session.add(d)
            db.session.commit()
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create diagnosis: {}'.format(e.messages))
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
            # For validation only
            d = DiagnosisSchema(strict=True).load(body).data
            # Deserialize
            d1.external_id = body.get('external_id')
            d1.diagnosis = body.get('diagnosis')
            d1.age_at_event_days = body.get('age_at_event_days')
            d1.participant_id = body.get('participant_id')
            db.session.commit()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('diagnosis', kf_id))
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not update diagnosis: {}'.format(e.messages))
        # Database error
        except IntegrityError as e:
            db.session.rollback()
            print(e)
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
        try:
            d = Diagnosis.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('diagnosis', kf_id))

        db.session.delete(d)
        db.session.commit()

        return DiagnosisSchema(200, 'diagnosis {} deleted'
                               .format(d.kf_id)).jsonify(d), 200
