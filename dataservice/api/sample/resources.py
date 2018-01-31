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
from dataservice.api.sample.models import Sample
from dataservice.api.sample.schemas import SampleSchema


class SampleAPI(MethodView):
    """
    Sample REST API
    """

    def get(self, kf_id):
        """
        Get a sample by id or get all samples

        Get a sample by Kids First id or get all samples if
        Kids First id is None
        """
        # Get all
        if kf_id is None:
            s = Sample.query.all()
            return SampleSchema(many=True).jsonify(s)
        # Get one
        else:
            try:
                s = Sample.query.filter_by(kf_id=kf_id).one()
            # Not found in database
            except NoResultFound:
                abort(404, 'could not find {} `{}`'
                      .format('sample', kf_id))
            return SampleSchema().jsonify(s)

    def post(self):
        """
        Create a new sample
        """
        body = request.json
        try:
            # Deserialize
            s = SampleSchema(strict=True).load(body).data
            # Add to and save in database
            db.session.add(s)
            db.session.commit()
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create sample: {}'.format(e.messages))
        # Database error
        except IntegrityError as e:
            db.session.rollback()
            context = {'method': 'create', 'entity': 'sample',
                       'ref_entity': 'participant', 'exception': e}
            abort(400, handle_integrity_error(**context))

        return SampleSchema(201, 'sample {} created'
                            .format(s.kf_id)).jsonify(s), 201

    def put(self, kf_id):
        """
        Update existing sample

        Update an existing sample given a Kids First id
        """
        body = request.json
        try:
            # Check if sample exists
            s1 = Sample.query.filter_by(kf_id=kf_id).one()
            # For validation only
            s = SampleSchema(strict=True).load(body).data
            # Deserialize
            s1.external_id = body.get('external_id')
            s1.tissue_type = body.get('tissue_type')
            s1.composition = body.get('composition')
            s1.anatomical_site = body.get('anatomical_site')
            s1.tumor_descriptor = body.get('tumor_descriptor')
            s1.aliquots = body.get('aliquots', [])
            s1.age_at_event_days = body.get('age_at_event_days')
            s1.participant_id = body.get('participant_id')
            db.session.commit()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('sample', kf_id))
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not update sample: {}'.format(e.messages))
        # Database error
        except IntegrityError as e:
            db.session.rollback()
            context = {'method': 'update', 'entity': 'sample',
                       'ref_entity': 'participant', 'exception': e}
            abort(400, handle_integrity_error(**context))

        return SampleSchema(200, 'sample {} updated'
                            .format(s1.kf_id)).jsonify(s1), 200

    def delete(self, kf_id):
        """
        Delete sample by id

        Deletes a sample given a Kids First id
        """
        try:
            s = Sample.query.filter_by(kf_id=kf_id).one()
        # Not found in database
        except NoResultFound:
            abort(404, 'could not find {} `{}`'.format('sample', kf_id))

        db.session.delete(s)
        db.session.commit()

        return SampleSchema(200, 'sample {} deleted'
                            .format(s.kf_id)).jsonify(s), 200
