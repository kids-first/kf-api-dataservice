from flask import abort, request
from marshmallow import ValidationError

from dataservice.extensions import db, indexd
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
        pager = Pagination(q, after, limit)

        # For each genomic_file, get indexd properties and merge into obj
        for gf in pager.items:
            indexd.merge_properties(gf.uuid, gf)

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

        # Register genomic file with indexd
        indexd.register_record(gf)

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
        # Get genomic_file from db
        genomic_file = GenomicFile.query.get(kf_id)
        if genomic_file is None:
            abort(404, 'could not find {} `{}`'
                  .format('GenomicFile', kf_id))

        # Get genomic_file indexd properties and merge into obj
        indexd.merge_properties(genomic_file.uuid, genomic_file)

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
                  .format('GenomicFile', kf_id))

        # Get genomic_file indexd properties and merge into obj
        indexd.merge_properties(gf.uuid, gf)

        # Update genomic_file with properties in patch request
        try:
            gf = GenomicFileSchema(strict=True).load(body, instance=gf,
                                                     partial=True).data
        except ValidationError as err:
            abort(400,
                  'could not update genomic_file: {}'.format(err.messages))

        # Send update request to indexd
        indexd.update(gf)

        # Save updated genomic_file in db
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
            abort(404, 'could not find {} `{}`'.format('GenomicFile', kf_id))

        # Delete genomic file from indexd
        indexd.delete_record(gf)

        db.session.delete(gf)
        db.session.commit()

        return GenomicFileSchema(
            200, 'genomic_file {} deleted'.format(gf.kf_id)
        ).jsonify(gf), 200
