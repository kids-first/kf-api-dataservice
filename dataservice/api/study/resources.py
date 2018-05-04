from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.study.models import Study
from dataservice.api.study.schemas import StudySchema
from dataservice.api.common.views import CRUDView


class StudyListAPI(CRUDView):
    """
    Study API
    """
    endpoint = 'studies_list'
    rule = '/studies'
    schemas = {'Study': StudySchema}

    @paginated
    def get(self, after, limit):
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
        q = (Study.query.options(joinedload(Study.study_files)
                                 .load_only('kf_id'))
             .options(joinedload(Study.participants)
                      .load_only('kf_id')))

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

        db.session.delete(st)
        db.session.commit()

        return StudySchema(
            200, 'study {} deleted'.format(st.kf_id)
        ).jsonify(st), 200
