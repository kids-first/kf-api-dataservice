from flask import abort, request
from marshmallow import ValidationError

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.phenotype.schemas import PhenotypeSchema
from dataservice.api.common.views import CRUDView


class PhenotypeListAPI(CRUDView):
    """
    Phenotype REST API
    """
    endpoint = 'phenotypes_list'
    rule = '/phenotypes'
    schemas = {'Phenotype': PhenotypeSchema}

    @paginated
    def get(self, after, limit):
        """
        Get all phenotypes
        ---
        description: Get all phenotypes
        template:
          path:
            get_list.yml
          properties:
            resource:
              Phenotype
        """
        q = Phenotype.query

        # Filter by study
        from dataservice.api.participant.models import Participant
        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(Participant.phenotypes)
                 .filter(Participant.study_id == study_id))

        return (PhenotypeSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new phenotype
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Phenotype
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            p = PhenotypeSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create phenotype: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(p)
        db.session.commit()

        return PhenotypeSchema(201, 'phenotype {} created'
                               .format(p.kf_id)).jsonify(p), 201


class PhenotypeAPI(CRUDView):
    """
    Phenotype REST API
    """
    endpoint = 'phenotypes'
    rule = '/phenotypes/<string:kf_id>'
    schemas = {'Phenotype': PhenotypeSchema}

    def get(self, kf_id):
        """
        Get a phenotype by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Phenotype
        """
        # Get one
        p = Phenotype.query.get(kf_id)
        # Not found in database
        if p is None:
            abort(404, 'could not find {} `{}`'
                  .format('phenotype', kf_id))
        return PhenotypeSchema().jsonify(p)

    def patch(self, kf_id):
        """
        Update an existing phenotype

        Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Phenotype
        """
        body = request.get_json(force=True) or {}
        # Check if phenotype exists
        p = Phenotype.query.get(kf_id)
        # Not found in database
        if p is None:
            abort(404, 'could not find {} `{}`'.format('phenotype', kf_id))

        # Validation only
        try:
            p = PhenotypeSchema(strict=True).load(body, instance=p,
                                                  partial=True).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not update phenotype: {}'.format(e.messages))

        # Save to database
        db.session.add(p)
        db.session.commit()

        return PhenotypeSchema(200, 'phenotype {} updated'
                               .format(p.kf_id)).jsonify(p), 200

    def delete(self, kf_id):
        """
        Delete phenotype by id

        Deletes a phenotype given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Phenotype
        """

        # Check if phenotype exists
        p = Phenotype.query.get(kf_id)
        # Not found in database
        if p is None:
            abort(404, 'could not find {} `{}`'.format('phenotype', kf_id))

        # Save in database
        db.session.delete(p)
        db.session.commit()

        return PhenotypeSchema(200, 'phenotype {} deleted'
                               .format(p.kf_id)).jsonify(p), 200
