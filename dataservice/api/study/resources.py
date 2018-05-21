from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.study.models import Study
from dataservice.api.study.schemas import StudySchema
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class StudyListAPI(CRUDView):
    """
    Study API
    """
    endpoint = 'studies_list'
    rule = '/studies'
    schemas = {'Study': StudySchema}

    @paginated
    @use_args(filter_schema_factory(StudySchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get a paginated studies
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              Study
        """
        q = (Study.query
             .filter_by(**filter_params))

        return (StudySchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new study
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              Study
        """
        body = request.get_json(force=True)
        try:
            st = StudySchema(strict=True).load(body).data
        except ValidationError as err:
            abort(400, 'could not create study: {}'.format(err.messages))

        db.session.add(st)
        db.session.commit()
        return StudySchema(
            201, 'study {} created'.format(st.kf_id)
        ).jsonify(st), 201


class StudyAPI(CRUDView):
    """
    Study API
    """
    endpoint = 'studies'
    rule = '/studies/<string:kf_id>'
    schemas = {'Study': StudySchema}

    def get(self, kf_id):
        """
        Get a study by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              Study
        """
        st = Study.query.get(kf_id)
        if st is None:
            abort(404, 'could not find {} `{}`'
                  .format('study', kf_id))
        return StudySchema().jsonify(st)

    def patch(self, kf_id):
        """
        Update an existing study. Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              Study
        """
        body = request.get_json(force=True)
        st = Study.query.get(kf_id)
        if st is None:
            abort(404, 'could not find {} `{}`'
                  .format('study', kf_id))

        try:
            st = (StudySchema(strict=True).load(body, instance=st,
                                                partial=True).data)
        except ValidationError as err:
            abort(400, 'could not update study: {}'.format(err.messages))

        db.session.add(st)
        db.session.commit()

        return StudySchema(
            200, 'study {} updated'.format(st.kf_id)
        ).jsonify(st), 200

    def delete(self, kf_id):
        """
        Delete study by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              Study
        """
        st = Study.query.get(kf_id)
        if st is None:
            abort(404, 'could not find {} `{}`'.format('study', kf_id))

        # -- Delete records from indexd - -
        _delete_indexd_gfs(kf_id)
        _delete_indexd_sfs(kf_id)

        # Delete study - will execute db cascade delete
        Study.query.filter_by(kf_id=kf_id).delete()
        db.session.commit()

        # -- Delete orphans ---
        # Families
        from dataservice.api.family.models import Family
        (db.session.query(Family)
         .filter(~Family.participants.any())).delete(
            synchronize_session=False)

        # Sequencing experiments
        from dataservice.api.sequencing_experiment.models import (
            SequencingExperiment
        )
        (db.session.query(SequencingExperiment)
         .filter(~SequencingExperiment.genomic_files.any())).delete(
            synchronize_session=False)

        db.session.commit()

        return StudySchema(
            200, 'study {} deleted'.format(st.kf_id)
        ).jsonify(st), 200


def _delete_indexd_gfs(study_id):
    """
    Delete genomic files for a study from indexd
    """
    from dataservice.api.participant.models import Participant
    from dataservice.api.biospecimen.models import Biospecimen
    from dataservice.api.genomic_file.models import GenomicFile
    from dataservice.api.common.model import delete_indexd
    # GenomicFiles for this study
    gfs = (GenomicFile.query.join(GenomicFile.biospecimen)
           .join(Biospecimen.participant)
           .filter(Participant.study_id == study_id)).all()
    # Delete from indexd
    [delete_indexd(None, None, gf) for gf in gfs]


def _delete_indexd_sfs(study_id):
    """
    Delete study files for a study from indexd
    """
    from dataservice.api.study_file.models import StudyFile
    from dataservice.api.common.model import delete_indexd
    sfs = StudyFile.query.filter_by(study_id=study_id).all()
    [delete_indexd(None, None, sf) for sf in sfs]
