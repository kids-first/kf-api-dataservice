from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.biospecimen.schemas import BiospecimenSchema
from dataservice.api.common.views import CRUDView


class BiospecimenListAPI(CRUDView):
    """
    Biospecimen REST API
    """
    endpoint = 'biospecimens_list'
    rule = '/biospecimens'
    schemas = {'Biospecimen': BiospecimenSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all biospecimens
        ---
        description: Get all biospecimens
        template:
          path:
            get_list.yml
          properties:
            resource:
              Biospecimen
        """
        q = Biospecimen.query.options(joinedload(Biospecimen.genomic_files)
                                      .load_only('kf_id'))

        # Filter by study
        from dataservice.api.participant.models import Participant
        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(Participant.biospecimens)
                 .filter(Participant.study_id == study_id))

        return (BiospecimenSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new biospecimen
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Biospecimen
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            s = BiospecimenSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create biospecimen: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(s)
        db.session.commit()

        return BiospecimenSchema(201, 'biospecimen {} created'
                                 .format(s.kf_id)).jsonify(s), 201


class BiospecimenAPI(CRUDView):
    """
    Biospecimen REST API
    """
    endpoint = 'biospecimens'
    rule = '/biospecimens/<string:kf_id>'
    schemas = {'Biospecimen': BiospecimenSchema}

    def get(self, kf_id):
        """
        Get biospecimens by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Biospecimen
        """
        sa = Biospecimen.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen', kf_id))
        return BiospecimenSchema().jsonify(sa)

    def patch(self, kf_id):
        """
        Update an existing biospecimen. Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Biospecimen
        """
        sa = Biospecimen.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            sa = BiospecimenSchema(strict=True).load(body, instance=sa,
                                                     partial=True).data
        except ValidationError as err:
            abort(400, 'could not update biospecimen: {}'.format(err.messages))

        db.session.add(sa)
        db.session.commit()

        return BiospecimenSchema(
            200, 'biospecimen {} updated'.format(sa.kf_id)
        ).jsonify(sa), 200

    def delete(self, kf_id):
        """
        Delete biospecimen by id

        Deletes a biospecimen given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Biospecimen
        """

        # Check if biospecimen exists
        sa = Biospecimen.query.get(kf_id)
        if sa is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen', kf_id))

        # Save in database
        db.session.delete(sa)
        db.session.commit()

        return BiospecimenSchema(200, 'biospecimen {} deleted'
                                 .format(sa.kf_id)).jsonify(sa), 200
