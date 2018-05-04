from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.investigator.models import Investigator
from dataservice.api.investigator.schemas import InvestigatorSchema
from dataservice.api.common.views import CRUDView


class InvestigatorListAPI(CRUDView):
    """
    Investigator API
    """
    endpoint = 'investigators_list'
    rule = '/investigators'
    schemas = {'Investigator': InvestigatorSchema}

    @paginated
    def get(self, after, limit):
        """
        Get a paginated investigators
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              Investigator
        """
        q = Investigator.query.options(
            joinedload(Investigator.studies)
            .load_only('kf_id'))

        # Filter by study
        from dataservice.api.study.models import Study
        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(Investigator.studies)
                 .filter(Study.kf_id == study_id))

        return (InvestigatorSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new investigator
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Investigator
        """
        body = request.get_json(force=True)
        try:
            inv = InvestigatorSchema(strict=True).load(body).data
        except ValidationError as err:
            abort(400,
                  'could not create investigator: {}'.format(err.messages))

        db.session.add(inv)
        db.session.commit()
        return InvestigatorSchema(
            201, 'investigator {} created'.format(inv.kf_id)
        ).jsonify(inv), 201


class InvestigatorAPI(CRUDView):
    """
    Investigator API
    """
    endpoint = 'investigators'
    rule = '/investigators/<string:kf_id>'
    schemas = {'Investigator': InvestigatorSchema}

    def get(self, kf_id):
        """
        Get a investigator by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Investigator
        """
        investigator = Investigator.query.get(kf_id)
        if investigator is None:
            abort(404, 'could not find {} `{}`'
                  .format('investigator', kf_id))
        return InvestigatorSchema().jsonify(investigator)

    def patch(self, kf_id):
        """
        Update an existing investigator. Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Investigator
        """
        body = request.get_json(force=True)
        inv = Investigator.query.get(kf_id)
        if inv is None:
            abort(404, 'could not find {} `{}`'
                  .format('investigator', kf_id))

        try:
            inv = (InvestigatorSchema(strict=True).load(body, instance=inv,
                                                        partial=True).data)
        except ValidationError as err:
            abort(400, 'could not update investigator: {}'
                  .format(err.messages))

        db.session.commit()

        return InvestigatorSchema(
            200, 'investigator {} updated'.format(inv.kf_id)
        ).jsonify(inv), 200

    def delete(self, kf_id):
        """
        Delete investigator by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Investigator
        """
        inv = Investigator.query.get(kf_id)
        if inv is None:
            abort(404, 'could not find {} `{}`'.format('investigator', kf_id))

        db.session.delete(inv)
        db.session.commit()

        return InvestigatorSchema(
            200, 'investigator {} deleted'.format(inv.kf_id)
        ).jsonify(inv), 200
