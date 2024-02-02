from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.biospecimen.models import (
    Biospecimen,
    BiospecimenDiagnosis,
    BiospecimenGenomicFile
)
from dataservice.api.biospecimen.schemas import (
    BiospecimenSchema,
    BiospecimenFilterSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class BiospecimenListAPI(CRUDView):
    """
    Biospecimen REST API
    """
    endpoint = 'biospecimens_list'
    rule = '/biospecimens'
    schemas = {'Biospecimen': BiospecimenSchema}

    @paginated
    @use_args(filter_schema_factory(BiospecimenFilterSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
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
        # Get and remove special filter params that are not attributes of model
        study_id = filter_params.pop('study_id', None)
        diagnosis_id = filter_params.pop('diagnosis_id', None)
        genomic_file_id = filter_params.pop('genomic_file_id', None)

        # Get and remove any list type filter params that need to be
        # handled differently than others
        duo_ids = filter_params.pop('duo_ids', None)

        # Apply filter params
        q = (Biospecimen.query
             .filter_by(**filter_params))

        # Apply duo_ids filter
        # Get specimens whose duo ids list includes all values in duo_ids
        if duo_ids:
            duo_ids = [id_.strip() for id_ in duo_ids[0].split(',')]
            q = q.filter(Biospecimen.duo_ids.contains(duo_ids))

        # Apply study_id filter and diagnosis_id filter
        from dataservice.api.participant.models import Participant

        if study_id:
            q = (q.join(Participant.biospecimens)
                 .filter(Participant.study_id == study_id))
        if diagnosis_id:
            q = (q.join(BiospecimenDiagnosis)
                 .filter(BiospecimenDiagnosis.diagnosis_id == diagnosis_id))
        if genomic_file_id:
            q = (q.join(BiospecimenGenomicFile)
                 .filter(BiospecimenGenomicFile.genomic_file_id ==
                         genomic_file_id))

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
            biospecimen = BiospecimenSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create biospecimen: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(biospecimen)
        db.session.commit()

        return BiospecimenSchema(
            201, 'biospecimen {} created'.format(biospecimen.kf_id)
        ).jsonify(biospecimen), 201


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
        biospecimen = Biospecimen.query.get(kf_id)
        if biospecimen is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            biospecimen = BiospecimenSchema(strict=True).load(
                body, instance=biospecimen, partial=True
            ).data
        except ValidationError as err:
            abort(400, 'could not update biospecimen: {}'.format(err.messages))

        db.session.add(biospecimen)
        db.session.commit()

        return BiospecimenSchema(
            200, 'biospecimen {} updated'.format(biospecimen.kf_id)
        ).jsonify(biospecimen), 200

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
