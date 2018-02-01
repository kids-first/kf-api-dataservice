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
from dataservice.api.demographic.models import Demographic
from dataservice.api.demographic.schemas import DemographicSchema


class DemographicAPI(MethodView):
    """
    Demographic REST API
    """

    def get(self, kf_id):
        """
        Get a demographic by id or get all demographics

        Get a demographic by Kids First id or get all demographics if
        Kids First id is None
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
        """

        body = request.json

        # Deserialize
        try:
            d = DemographicSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create demographic: {}'.format(e.messages))

        # Add to and save in database
        try:
            db.session.add(d)
            db.session.commit()
        # Database error
        except IntegrityError as e:
            db.session.rollback()
            context = {'method': 'create', 'entity': 'demographic',
                       'ref_entity': 'participant', 'exception': e}
            abort(400, handle_integrity_error(**context))

        return DemographicSchema(201, 'demographic {} created'
                                 .format(d.kf_id)).jsonify(d), 201

    def put(self, kf_id):
        """
        Update existing demographic

        Update an existing demographic given a Kids First id
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
        try:
            db.session.commit()
        # Database error
        except IntegrityError as e:
            db.session.rollback()
            context = {'method': 'update', 'entity': 'demographic',
                       'ref_entity': 'participant', 'exception': e}
            abort(400, handle_integrity_error(**context))

        return DemographicSchema(200, 'demographic {} updated'
                                 .format(d1.kf_id)).jsonify(d1), 200

    def delete(self, kf_id):
        """
        Delete demographic by id

        Deletes a demographic given a Kids First id
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
