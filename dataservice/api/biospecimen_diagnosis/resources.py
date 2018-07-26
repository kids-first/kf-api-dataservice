from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.biospecimen_diagnosis.models import (
    BiospecimenDiagnosis
)
from dataservice.api.biospecimen_diagnosis.schemas import (
    BiospecimenDiagnosisSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class BiospecimenDiagnosisListAPI(CRUDView):
    """
    BiospecimenDiagnosis List API
    """
    endpoint = 'biospecimen_diagnoses_list'
    rule = '/biospecimen-diagnoses'
    schemas = {'BiospecimenDiagnosis': BiospecimenDiagnosisSchema}

    @paginated
    @use_args(filter_schema_factory(BiospecimenDiagnosisSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get a paginated biospecimen_diagnoses
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              BiospecimenDiagnosis
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        q = BiospecimenDiagnosis.query.filter_by(**filter_params)

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen

        if study_id:
            q = (q.join(BiospecimenDiagnosis.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id))

        return (BiospecimenDiagnosisSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new biospecimen_diagnosis
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              BiospecimenDiagnosis
        """
        body = request.get_json(force=True)
        try:
            bs_ds = (BiospecimenDiagnosisSchema(strict=True)
                     .load(body).data)
            print(bs_ds)
        except ValidationError as err:
            abort(400,
                  'could not create biospecimen_diagnosis: {}'
                  .format(err.messages))

        db.session.add(bs_ds)
        db.session.commit()
        return BiospecimenDiagnosisSchema(
            201, 'biospecimen_diagnosis {} created'.format(bs_ds.kf_id)
        ).jsonify(bs_ds), 201


class BiospecimenDiagnosisAPI(CRUDView):
    """
    BiospecimenDiagnosis API
    """
    endpoint = 'biospecimen_diagnoses'
    rule = '/biospecimen-diagnoses/<string:kf_id>'
    schemas = {'BiospecimenDiagnosis': BiospecimenDiagnosisSchema}

    def get(self, kf_id):
        """
        Get a biospecimen_diagnosis by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              BiospecimenDiagnosis
        """
        bs_ds = BiospecimenDiagnosis.query.get(kf_id)
        if bs_ds is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen_diagnosis', kf_id))

        return BiospecimenDiagnosisSchema().jsonify(bs_ds)

    def patch(self, kf_id):
        """
        Update an existing biospecimen_diagnosis. Allows partial update
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              BiospecimenDiagnosis
        """
        bs_ds = BiospecimenDiagnosis.query.get(kf_id)
        if bs_ds is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen_diagnosis', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            bs_ds = (BiospecimenDiagnosisSchema(strict=True)
                     .load(body, instance=bs_ds, partial=True).data)
        except ValidationError as err:
            abort(400,
                  'could not update biospecimen_diagnosis: {}'
                  .format(err.messages))

        db.session.add(bs_ds)
        db.session.commit()

        return BiospecimenDiagnosisSchema(
            200, 'biospecimen_diagnosis {} updated'.format(bs_ds.kf_id)
        ).jsonify(bs_ds), 200

    def delete(self, kf_id):
        """
        Delete biospecimen_diagnosis by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              BiospecimenDiagnosis
        """
        bs_ds = BiospecimenDiagnosis.query.get(kf_id)
        if bs_ds is None:
            abort(404, 'could not find {} `{}`'
                  .format('biospecimen_diagnosis', kf_id))

        db.session.delete(bs_ds)
        db.session.commit()

        return BiospecimenDiagnosisSchema(
            200, 'biospecimen_diagnosis {} deleted'.format(bs_ds.kf_id)
        ).jsonify(bs_ds), 200
