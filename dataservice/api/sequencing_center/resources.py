from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.sequencing_center.schemas import (
    SequencingCenterSchema
)
from dataservice.api.common.views import CRUDView


class SequencingCenterListAPI(CRUDView):
    """
    SequencingCenter REST API
    """
    endpoint = 'sequencing_centers_list'
    rule = '/sequencing-centers'
    schemas = {'SequencingCenter': SequencingCenterSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all sequencing_centers
        ---
        description: Get all sequencing_centers
        template:
          path:
            get_list.yml
          properties:
            resource:
              SequencingCenter
        """
        q = (SequencingCenter.query
             .options(joinedload(SequencingCenter.biospecimens)
                      .load_only('kf_id'))
             .options(joinedload(SequencingCenter.sequencing_experiments).
                      load_only('kf_id')))
        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(SequencingCenter.biospecimens)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id))

        return (SequencingCenterSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new sequencing_center
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              SequencingCenter
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            se = SequencingCenterSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create sequencing_center: {}'
                  .format(e.messages))

        # Add to and save in database
        db.session.add(se)
        db.session.commit()

        return SequencingCenterSchema(201,
                                      'sequencing_center {} created'
                                      .format(se.kf_id)).jsonify(se), 201


class SequencingCenterAPI(CRUDView):
    """
    SequencingCenter REST API
    """
    endpoint = 'sequencing_centers'
    rule = '/sequencing-centers/<string:kf_id>'
    schemas = {'SequencingCenter': SequencingCenterSchema}

    def get(self, kf_id):
        """
        Get a sequencing_center by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              SequencingCenter
        """
        # Get one
        se = SequencingCenter.query.get(kf_id)
        if se is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_center', kf_id))
        return SequencingCenterSchema().jsonify(se)

    def patch(self, kf_id):
        """
        Update an existing sequencing_center.

        Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              SequencingCenter
        """
        se = SequencingCenter.query.get(kf_id)
        if se is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_center', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            se = (SequencingCenterSchema(strict=True).
                  load(body, instance=se,
                       partial=True).data)
        except ValidationError as err:
            abort(400, 'could not update sequencing_center: {}'
                  .format(err.messages))

        db.session.add(se)
        db.session.commit()

        return SequencingCenterSchema(
            200, 'sequencing_center {} updated'.format(se.kf_id)
        ).jsonify(se), 200

    def delete(self, kf_id):
        """
        Delete sequencing_center by id

        Deletes a sequencing_center given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              SequencingCenter
        """

        # Check if sequencing_center exists
        se = SequencingCenter.query.get(kf_id)
        if se is None:
            abort(404, 'could not find {} `{}`'
                  .format('sequencing_center', kf_id))

        # Save in database
        db.session.delete(se)
        db.session.commit()

        return SequencingCenterSchema(200,
                                      'sequencing_center {} deleted'
                                      .format(se.kf_id)).jsonify(se), 200
