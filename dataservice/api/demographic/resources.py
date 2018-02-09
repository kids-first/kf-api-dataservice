from flask import abort, request
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.demographic.models import Demographic
from dataservice.api.demographic.schemas import DemographicSchema
from dataservice.api.common.views import CRUDView


class DemographicListAPI(CRUDView):
    """
    Demographic REST API
    """
    endpoint = 'demographics_list'
    rule = '/demographics'
    schemas = {'Demographic': DemographicSchema}

    def get(self):
        """
        Get a demographic by id or get all demographics
        ---
        description: Get demographics
        tags:
        - Demographic
        responses:
          200:
            description: Demographics found
            schema:
              $ref: '#/definitions/DemographicPaginated'
        """
        d = Demographic.query.all()
        return DemographicSchema(many=True).jsonify(d)

    def post(self):
        """
        Create a new demographic
        ---
        description: Create a new demographic
        tags:
        - Demographic
        parameters:
        - name: body
          in: body
          description: Content
          required: true
          schema:
            $ref: "#/definitions/Demographic"
        responses:
          201:
            description: Demographic created
            schema:
              $ref: '#/definitions/DemographicResponse'
          400:
            description: Could not create demographic
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
                      example: could not create demographic
                      type: string
        """

        body = request.json

        # Deserialize
        try:
            d = DemographicSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create demographic: {}'.format(e.messages))

        db.session.add(d)
        db.session.commit()

        return DemographicSchema(201, 'demographic {} created'
                                 .format(d.kf_id)).jsonify(d), 201


class DemographicAPI(CRUDView):
    """
    Demographic REST API
    """
    endpoint = 'demographics'
    rule = '/demographics/<string:kf_id>'
    schemas = {'Demographic': DemographicSchema}

    def get(self, kf_id):
        """
        Get a demographic by id or get all demographics

        Get a demographic by Kids First id or get all demographics if
        Kids First id is None
        ---
        description: Get demographic by id
        tags:
        - Demographic
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of demographic to return"
          required: true
          type: "string"
        responses:
          200:
            description: Demographic found
            schema:
              $ref: '#/definitions/DemographicResponse'
          404:
            description: Could not find demographic
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
                      example: could not find demographic `DZB048J5`
                      type: string
        """

        # Get all
        if kf_id is None:
            d = Demographic.query.all()
            return DemographicSchema(many=True).jsonify(d)
        # Get one
        else:
            try:
                d = Demographic.query.filter_by(kf_id=kf_id).one()
            # Not found in database
            except NoResultFound:
                abort(404, 'could not find {} `{}`'
                      .format('demographic', kf_id))
            return DemographicSchema().jsonify(d)

    def post(self):
        """
        Create a new demographic
        ---
        description: Create a new demographic
        tags:
        - Demographic
        parameters:
        - name: body
          in: body
          description: Content
          required: true
          schema:
            $ref: "#/definitions/Demographic"
        responses:
          201:
            description: Demographic created
            schema:
              $ref: '#/definitions/DemographicResponse'
          400:
            description: Could not create demographic
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
                      example: could not create demographic
                      type: string
        """

        body = request.json

        # Deserialize
        try:
            d = DemographicSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create demographic: {}'.format(e.messages))

        db.session.add(d)
        db.session.commit()

        return DemographicSchema(201, 'demographic {} created'
                                 .format(d.kf_id)).jsonify(d), 201

    def put(self, kf_id):
        """
        Update existing demographic

        Update an existing demographic given a Kids First id
        ---
        description: Update a demographic
        tags:
        - Demographic
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of demographic to return"
          required: true
          type: "string"
        - name: "body"
          in: "body"
          description: "Demographic identifier"
          required: true
          schema:
            $ref: "#/definitions/Demographic"
        responses:
          200:
            description: Demographic updated
            schema:
              $ref: '#/definitions/DemographicResponse'
          400:
            description: Could not update demographic
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
                      example: could not update demographic
                      type: string
          404:
            description: Could not find demographic
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
                      example: could not find demographic `DZB048J5`
                      type: string
        """
        body = request.json

        # Check if demographic exists
        try:
            d1 = Demographic.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('demographic', kf_id))

        # Validation only
        try:
            d = DemographicSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not update demographic: {}'.format(e.messages))

        # Deserialize
        d1.external_id = body.get('external_id')
        d1.race = body.get('race')
        d1.gender = body.get('gender')
        d1.ethnicity = body.get('ethnicity')
        d1.participant_id = body.get('participant_id')

        # Save to database
        db.session.commit()

        return DemographicSchema(200, 'demographic {} updated'
                                 .format(d1.kf_id)).jsonify(d1), 200

    def delete(self, kf_id):
        """
        Delete demographic by id

        Deletes a demographic given a Kids First id
        ---
        description: Delete a demographic by id
        tags:
        - Demographic
        parameters:
        - name: "kf_id"
          in: "path"
          description: "ID of demographic to delete"
          required: true
          type: "string"
        responses:
          200:
            description: Demographic deleted
            schema:
              $ref: '#/definitions/DemographicResponse'
          404:
            description: Could not find demographic
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
                      example: could not find demographic `DZB048J5`
                      type: string
        """
        # Check if demographic exists
        try:
            d = Demographic.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('demographic', kf_id))

        # Save in database
        db.session.delete(d)
        db.session.commit()

        return DemographicSchema(200, 'demographic {} deleted'
                                 .format(d.kf_id)).jsonify(d), 200
