from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.family.models import Family
from dataservice.api.family.schemas import FamilySchema
from dataservice.api.common.views import CRUDView


class FamilyListAPI(CRUDView):
    """
    Family API
    """
    endpoint = 'families_list'
    rule = '/families'
    schemas = {'Family': FamilySchema}

    @paginated
    def get(self, after, limit):
        """
        Get a paginated familys
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              Family
        """
        q = Family.query.options(joinedload(Family.participants)
                                 .load_only('kf_id'))

        # Filter by study
        from dataservice.api.participant.models import Participant
        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(Family.participants)
                 .filter(Participant.study_id == study_id)
                 .group_by(Family.kf_id))

        return (FamilySchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new family
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Family
        """
        body = request.get_json(force=True)
        try:
            fam = FamilySchema(strict=True).load(body).data
        except ValidationError as err:
            abort(400, 'could not create family: {}'.format(err.messages))

        db.session.add(fam)
        db.session.commit()
        return FamilySchema(
            201, 'family {} created'.format(fam.kf_id)
        ).jsonify(fam), 201


class FamilyAPI(CRUDView):
    """
    Family API
    """
    endpoint = 'families'
    rule = '/families/<string:kf_id>'
    schemas = {'Family': FamilySchema}

    def get(self, kf_id):
        """
        Get a family by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Family
        """
        fam = Family.query.get(kf_id)
        if fam is None:
            abort(404, 'could not find {} `{}`'
                  .format('family', kf_id))

        return FamilySchema().jsonify(fam)

    def patch(self, kf_id):
        """
        Update an existing family. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Family
        """
        fam = Family.query.get(kf_id)
        if fam is None:
            abort(404, 'could not find {} `{}`'
                  .format('family', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            fam = FamilySchema(strict=True).load(body, instance=fam,
                                                 partial=True).data
        except ValidationError as err:
            abort(400, 'could not update family: {}'.format(err.messages))

        db.session.add(fam)
        db.session.commit()

        return FamilySchema(
            200, 'family {} updated'.format(fam.kf_id)
        ).jsonify(fam), 200

    def delete(self, kf_id):
        """
        Delete family by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Family
        """
        fam = Family.query.get(kf_id)
        if fam is None:
            abort(404, 'could not find {} `{}`'
                  .format('family', kf_id))

        db.session.delete(fam)
        db.session.commit()

        return FamilySchema(
            200, 'family {} deleted'.format(fam.kf_id)
        ).jsonify(fam), 200
