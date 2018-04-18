from flask import abort, request
from marshmallow import ValidationError
from sqlalchemy.orm import Load

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.genomic_file.schemas import GenomicFileSchema
from dataservice.api.common.views import CRUDView


class GenomicFileListAPI(CRUDView):
    """
    GenomicFile API
    """
    endpoint = 'genomic_files_list'
    rule = '/genomic-files'
    schemas = {'GenomicFile': GenomicFileSchema}

    @paginated
    def get(self, after, limit):
        """
        Get paginated genomic_files

        Retrieves the genomic files stored in the datamodel, then fetch
        additional properties that are stored in indexd under the same uuid.
        ---
        template:
          path:
            get_list.yml
          properties:
            resource:
              GenomicFile
        """
        # Get a page of the data from the model first
        q = GenomicFile.query

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        study_id = request.args.get('study_id')
        if study_id:
            q = (q.join(GenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .options(Load(Participant).load_only("kf_id", "study_id"))
                 .filter(Participant.study_id == study_id))

        pager = Pagination(q, after, limit)
        keep = []
        refresh = True
        next_after = None
        # Continue updating the page until we get a page with no deleted files
        while (pager.total > 0 and refresh):
            refresh = False
            # Move the cursor ahead to the last valid file
            next_after = keep[-1].created_at if len(keep) > 0 else after
            # Number of results needed to fulfill the original limit
            remain = limit - len(keep)
            pager = Pagination(q, next_after, remain)

            for gf in pager.items:
                merged = gf.merge_indexd()
                if merged is not None:
                    keep.append(gf)
                else:
                    refresh = True

        # Replace original page's items with new list of valid files
        pager.items = keep
        pager.after = next_after if next_after else after

        return (GenomicFileSchema(many=True)
                .jsonify(pager))

    def post(self):
        """
        Create a new genomic_file
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              GenomicFile
        """
        try:
            gf = GenomicFileSchema(strict=True).load(request.json).data
        except ValidationError as err:
            abort(400,
                  'could not create genomic_file: {}'.format(err.messages))

        db.session.add(gf)
        db.session.commit()

        return GenomicFileSchema(
            201, 'genomic_file {} created'.format(gf.kf_id)
        ).jsonify(gf), 201


class GenomicFileAPI(CRUDView):
    """
    GenomicFile API
    """
    endpoint = 'genomic_files'
    rule = '/genomic-files/<string:kf_id>'
    schemas = {'GenomicFile': GenomicFileSchema}

    def get(self, kf_id):
        """
        Get a genomic file by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              GenomicFile
        """
        genomic_file = GenomicFile.query.get(kf_id)
        if genomic_file is None:
            abort(404, 'could not find {} `{}`'
                  .format('genomic_file', kf_id))

        # Merge will return None if the document wasnt found in indexd
        merge = genomic_file.merge_indexd()
        if merge is None:
            abort(404, 'could not find {} `{}`'
                  .format('genomic_file', kf_id))

        sch = GenomicFileSchema(many=False)
        return sch.jsonify(genomic_file)

    def patch(self, kf_id):
        """
        Update an existing genomic_file
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              GenomicFile
        """
        body = request.json or {}
        gf = GenomicFile.query.get(kf_id)
        if gf is None:
            abort(404, 'could not find {} `{}`'
                  .format('genomic_file', kf_id))

        # Fetch fields from indexd first
        merge = gf.merge_indexd()
        if merge is None:
            abort(404, 'could not find {} `{}`'
                  .format('genomic_file', kf_id))

        # Deserialization will require this field and won't merge automatically
        if 'sequencing_experiment_id' not in body:
            body['sequencing_experiment_id'] = gf.sequencing_experiment_id

        try:
            gf = GenomicFileSchema(strict=True).load(body, instance=gf,
                                                     partial=True).data
        except ValidationError as err:
            abort(400,
                  'could not update genomic_file: {}'.format(err.messages))

        db.session.add(gf)
        db.session.commit()

        return GenomicFileSchema(
            200, 'genomic_file {} updated'.format(gf.kf_id)
        ).jsonify(gf), 200

    def delete(self, kf_id):
        """
        Delete genomic_file by id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              GenomicFile
        """
        gf = GenomicFile.query.get(kf_id)
        if gf is None:
            abort(404, 'could not find {} `{}`'.format('genomic_file', kf_id))

        db.session.delete(gf)
        db.session.commit()

        return GenomicFileSchema(
            200, 'genomic_file {} deleted'.format(gf.kf_id)
        ).jsonify(gf), 200
