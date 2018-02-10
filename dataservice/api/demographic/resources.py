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
        Get all demographics
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              Demographic
        """
        d = Demographic.query.all()
        return DemographicSchema(many=True).jsonify(d)

    def post(self):
        """
        Create a new demographic
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Demographic
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
        Get a demographic by id

        Get a demographic by Kids First id or get all demographics if
        Kids First id is None
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Demographic
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

    def put(self, kf_id):
        """
        Update existing demographic

        Update an existing demographic given a Kids First id
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Demographic
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
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Demographic
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
