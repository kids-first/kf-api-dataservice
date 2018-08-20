from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.diagnosis.schemas import (
    DiagnosisSchema,
    DiagnosisFilterSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class DiagnosisListAPI(CRUDView):
    """
    Diagnosis REST API
    """
    endpoint = 'diagnoses_list'
    rule = '/diagnoses'
    schemas = {'Diagnosis': DiagnosisSchema}

    @paginated
    @use_args(filter_schema_factory(DiagnosisFilterSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get all diagnoses
        ---
        description: Get all diagnoses
        template:
          path:
            get_list.yml
          properties:
            resource:
              Diagnosis
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        from dataservice.api.biospecimen.models import BiospecimenDiagnosis
        biospecimen_id = filter_params.pop('biospecimen_id', None)
        # # Apply entity filter params
        q = Diagnosis.query.filter_by(**filter_params)
        if biospecimen_id:
            q = q.join(Diagnosis.biospecimens).\
                filter(BiospecimenDiagnosis.biospecimen_id == biospecimen_id)

        # Apply study_id filter
        from dataservice.api.participant.models import Participant
        if study_id:
            q = (q.join(Participant.diagnoses)
                 .filter(Participant.study_id == study_id))

        return (DiagnosisSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new diagnosis
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Diagnosis
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            d = DiagnosisSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create diagnosis: {}'.format(e.messages))

        # Add to and save in database
        db.session.add(d)
        db.session.commit()

        return DiagnosisSchema(201, 'diagnosis {} created'
                               .format(d.kf_id)).jsonify(d), 201


class DiagnosisAPI(CRUDView):
    """
    Diagnosis REST API
    """
    endpoint = 'diagnoses'
    rule = '/diagnoses/<string:kf_id>'
    schemas = {'Diagnosis': DiagnosisSchema}

    def get(self, kf_id):
        """
        Get a diagnosis by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Diagnosis
        """
        # Get one
        dg = Diagnosis.query.get(kf_id)
        if dg is None:
            abort(404, 'could not find {} `{}`'
                  .format('diagnosis', kf_id))
        return DiagnosisSchema().jsonify(dg)

    def patch(self, kf_id):
        """
        Update an existing diagnosis. Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Diagnosis
        """
        dg = Diagnosis.query.get(kf_id)
        if dg is None:
            abort(404, 'could not find {} `{}`'
                  .format('diagnosis', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            dg = DiagnosisSchema(strict=True).load(body, instance=dg,
                                                   partial=True).data
        except ValidationError as err:
            abort(400, 'could not update diagnosis: {}'.format(err.messages))

        db.session.add(dg)
        db.session.commit()

        return DiagnosisSchema(
            200, 'diagnosis {} updated'.format(dg.kf_id)
        ).jsonify(dg), 200

    def delete(self, kf_id):
        """
        Delete diagnosis by id

        Deletes a diagnosis given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Diagnosis
        """

        # Check if diagnosis exists
        dg = Diagnosis.query.get(kf_id)
        if dg is None:
            abort(404, 'could not find {} `{}`'
                  .format('diagnosis', kf_id))

        # Save in database
        db.session.delete(dg)
        db.session.commit()

        return DiagnosisSchema(200, 'diagnosis {} deleted'
                               .format(dg.kf_id)).jsonify(dg), 200
