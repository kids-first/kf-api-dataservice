from flask import abort, request
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.sample.models import Sample
from dataservice.api.sample.schemas import SampleSchema
from dataservice.api.common.views import CRUDView


class SampleListAPI(CRUDView):
    """
    Sample REST API
    """
    endpoint = 'samples_list'
    rule = '/samples'
    schemas = {'Sample': SampleSchema}

    def get(self):
        """
        Get all samples
        ---
        description: Get samples
        tags:
        - Sample
        responses:
          200:
            description: Samples found
            schema:
              $ref: '#/definitions/SamplePaginated'
        """
        s = Sample.query.all()
        return SampleSchema(many=True).jsonify(s)

    def post(self):
        """
        Create a new sample
        ---
        description: Create a new sample
        tags:
        - Sample
        parameters:
        - name: body
          in: body
          description: Content
          required: true
          schema:
            $ref: "#/definitions/Sample"
        responses:
          201:
            description: Sample created
            schema:
              $ref: '#/definitions/SampleResponse'
          400:
            description: Could not create sample
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
                      example: could not create sample
                      type: string
        """

        body = request.json

        # Deserialize
        try:
            s = SampleSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create sample: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(s)
        db.session.commit()

        return SampleSchema(201, 'sample {} created'
                            .format(s.kf_id)).jsonify(s), 201


class SampleAPI(CRUDView):
    """
    Sample REST API
    """
    endpoint = 'samples'
    rule = '/samples/<string:kf_id>'
    schemas = {'Sample': SampleSchema}

    def get(self, kf_id):
        """
        Get samples by id
        ---
        description: Get sample by id
        tags:
        - Sample
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of sample to return"
          required: true
          type: "string"
        responses:
          200:
            description: Sample found
            schema:
              $ref: '#/definitions/SampleResponse'
          404:
            description: Could not find sample
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
                      example: could not find sample `DZB048J5`
                      type: string
        """
        try:
            s = Sample.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'
                  .format('sample', kf_id))
        return SampleSchema().jsonify(s)

    def put(self, kf_id):
        """
        Update existing sample

        Update an existing sample given a Kids First id
        ---
        description: Update a sample
        tags:
        - Sample
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of sample to return"
          required: true
          type: "string"
        - name: "body"
          in: "body"
          description: "Sample identifier"
          required: true
          schema:
            $ref: "#/definitions/Sample"
        responses:
          200:
            description: Sample updated
            schema:
              $ref: '#/definitions/SampleResponse'
          400:
            description: Could not update sample
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
                      example: could not update sample
                      type: string
          404:
            description: Could not find sample
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
                      example: could not find sample `DZB048J5`
                      type: string
        """
        body = request.json

        # Check if sample exists
        try:
            s1 = Sample.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('sample', kf_id))

        # Validation only
        try:
            s = SampleSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not update sample: {}'.format(e.messages))

        # Deserialize
        s1.external_id = body.get('external_id')
        s1.tissue_type = body.get('tissue_type')
        s1.composition = body.get('composition')
        s1.anatomical_site = body.get('anatomical_site')
        s1.tumor_descriptor = body.get('tumor_descriptor')
        s1.aliquots = body.get('aliquots', [])
        s1.age_at_event_days = body.get('age_at_event_days')
        s1.participant_id = body.get('participant_id')

        # Save to database
        db.session.commit()

        return SampleSchema(200, 'sample {} updated'
                            .format(s1.kf_id)).jsonify(s1), 200

    def delete(self, kf_id):
        """
        Delete sample by id

        Deletes a sample given a Kids First id
        ---
        description: Delete a sample by id
        tags:
        - Sample
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of sample to delete"
          required: true
          type: "string"
        responses:
          200:
            description: Sample deleted
            schema:
              $ref: '#/definitions/SampleResponse'
          404:
            description: Could not find sample
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
                      example: could not find sample `DZB048J5`
                      type: string
        """

        # Check if sample exists
        try:
            s = Sample.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('sample', kf_id))

        # Save in database
        db.session.delete(s)
        db.session.commit()

        return SampleSchema(200, 'sample {} deleted'
                            .format(s.kf_id)).jsonify(s), 200
