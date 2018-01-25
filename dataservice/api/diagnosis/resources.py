from flask import (
    abort,
    request
)
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.diagnosis.schemas import DiagnosisSchema


class DiagnosisListAPI(MethodView):
    """
    Diagnosis REST API
    """

    def get(self):
        """
        Get a diagnosis by id or get all diagnoses

        Get a diagnosis by Kids First id or get all diagnoses if
        Kids First id is None
        ---
        description: Get diagnoses
        tags:
        - Diagnosis
        responses:
          200:
            description: Diagnoses found
            schema:
              $ref: '#/definitions/DiagnosisPaginated'
        """
        d = Diagnosis.query.all()
        return DiagnosisSchema(many=True).jsonify(d)

    def post(self):
        """
        Create a new diagnosis
        ---
        description: Create a new diagnosis
        tags:
        - Diagnosis
        parameters:
        - name: body
          in: body
          description: Content
          required: true
          schema:
            $ref: "#/definitions/Diagnosis"
        responses:
          201:
            description: Diagnosis created
            schema:
              $ref: '#/definitions/DiagnosisResponse'
          400:
            description: Could not create diagnosis
            schema:
              type: object
              properties:
                _status:
                  type: object
                  properties:
                    code:
                      example: 400
                      type: integer
                    message:
                      example: could not create diagnosis
                      type: string
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


class DiagnosisAPI(MethodView):
    """
    Diagnosis REST API
    """

    def get(self, kf_id):
        """
        Get a diagnosis by id or get all diagnoses

        Get a diagnosis by Kids First id or get all diagnoses if
        Kids First id is None
        ---
        description: Get diagnosis by id
        tags:
        - Diagnosis
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of diagnosis to return"
          required: true
          type: "string"
        responses:
          200:
            description: Diagnosis found
            schema:
              $ref: '#/definitions/DiagnosisResponse'
          404:
            description: Could not find diagnosis
            schema:
              type: object
              properties:
                _status:
                  type: object
                  properties:
                    code:
                      example: 404
                      type: integer
                    message:
                      example: could not find diagnosis `DZB048J5`
                      type: string
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
        description: Update a diagnosis
        tags:
        - Diagnosis
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of diagnosis to return"
          required: true
          type: "string"
        - name: "body"
          in: "body"
          description: "Diagnosis identifier"
          required: true
          schema:
            $ref: "#/definitions/Diagnosis"
        responses:
          200:
            description: Diagnosis updated
            schema:
              $ref: '#/definitions/DiagnosisResponse'
          400:
            description: Could not update diagnosis
            schema:
              type: object
              properties:
                _status:
                  type: object
                  properties:
                    code:
                      example: 400
                      type: integer
                    message:
                      example: could not update diagnosis
                      type: string
          404:
            description: Could not find diagnosis
            schema:
              type: object
              properties:
                _status:
                  type: object
                  properties:
                    code:
                      example: 404
                      type: integer
                    message:
                      example: could not find diagnosis `DZB048J5`
                      type: string
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
        db.session.commit()

        return DiagnosisSchema(200, 'diagnosis {} updated'
                               .format(d1.kf_id)).jsonify(d1), 200

    def delete(self, kf_id):
        """
        Delete diagnosis by id

        Deletes a diagnosis given a Kids First id
        ---
        description: Delete a diagnosis by id
        tags:
        - Diagnosis
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of diagnosis to delete"
          required: true
          type: "string"
        responses:
          200:
            description: Diagnosis deleted
            schema:
              $ref: '#/definitions/DiagnosisResponse'
          404:
            description: Could not find diagnosis
            schema:
              type: object
              properties:
                _status:
                  type: object
                  properties:
                    code:
                      example: 404
                      type: integer
                    message:
                      example: could not find diagnosis `DZB048J5`
                      type: string
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
