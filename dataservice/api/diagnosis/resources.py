from flask import abort, request
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.diagnosis.schemas import DiagnosisSchema
from dataservice.api.common.views import CRUDView


class DiagnosisListAPI(CRUDView):
    """
    Diagnosis REST API
    """
    endpoint = 'diagnoses_list'
    rule = '/diagnoses'
    schemas = {'Diagnosis': DiagnosisSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all diagnoses
        ---
        description: Get all diagnoses
        template:
          path:
            get_list.yml
          properties:
            resource:
              Diagnosis
        """
        q = Diagnosis.query

        return (DiagnosisSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new diagnosis
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Diagnosis
        """

        body = request.json

        # Deserialize
        try:
            d = DiagnosisSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create diagnosis: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(d)
        db.session.commit()

        return DiagnosisSchema(201, 'diagnosis {} created'
                               .format(d.kf_id)).jsonify(d), 201


class DiagnosisAPI(CRUDView):
    """
    Diagnosis REST API
    """
    endpoint = 'diagnoses'
    rule = '/diagnoses/<string:kf_id>'
    schemas = {'Diagnosis': DiagnosisSchema}

    def get(self, kf_id):
        """
        Get a diagnosis by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Diagnosis
        """
        # Get one
        try:
            d = Diagnosis.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'
                  .format('diagnosis', kf_id))
        return DiagnosisSchema().jsonify(d)

    def put(self, kf_id):
        """
        Update existing diagnosis

        Update an existing diagnosis given a Kids First id
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Diagnosis
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
        d1.diagnosis_category = body.get('diagnosis_category')
        d1.tumor_location = body.get('tumor_location')
        d1.age_at_event_days = body.get('age_at_event_days')
        d1.participant_id = body.get('participant_id')

        # Save to database
        db.session.commit()

        return DiagnosisSchema(200, 'diagnosis {} updated'
                               .format(d1.kf_id)).jsonify(d1), 200

    def delete(self, kf_id):
        """
        Delete diagnosis by id

        Deletes a diagnosis given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Diagnosis
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
