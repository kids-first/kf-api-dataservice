from flask import abort, request
from marshmallow import ValidationError
from webargs.flaskparser import use_args

from dataservice.extensions import db
from dataservice.api.common.pagination import paginated, Pagination
from dataservice.api.read_group.models import (
    ReadGroup,
    ReadGroupGenomicFile
)
from dataservice.api.read_group.schemas import (
    ReadGroupSchema,
    ReadGroupFilterSchema
)
from dataservice.api.common.views import CRUDView
from dataservice.api.common.schemas import filter_schema_factory


class ReadGroupListAPI(CRUDView):
    """
    ReadGroup REST API
    """
    endpoint = 'read_groups_list'
    rule = '/read-groups'
    schemas = {'ReadGroup': ReadGroupSchema}

    @paginated
    @use_args(filter_schema_factory(ReadGroupFilterSchema),
              locations=('query',))
    def get(self, filter_params, after, limit):
        """
        Get all read_groups
        ---
        description: Get all read_groups
        template:
          path:
            get_list.yml
          properties:
            resource:
              ReadGroup
        """
        # Get study id and remove from model filter params
        study_id = filter_params.pop('study_id', None)

        # Get genomic file id and remove from model filter params
        genomic_file_id = filter_params.pop('genomic_file_id', None)

        # Apply model filter params
        q = ReadGroup.query.filter_by(**filter_params)

        # Filter by study
        from dataservice.api.participant.models import Participant
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.genomic_file.models import GenomicFile
        from dataservice.api.biospecimen_genomic_file.models import (
            BiospecimenGenomicFile
        )
        if study_id:
            q = (q.join(ReadGroup.read_group_genomic_files)
                 .join(ReadGroupGenomicFile.genomic_file)
                 .join(GenomicFile.biospecimen_genomic_files)
                 .join(BiospecimenGenomicFile.biospecimen)
                 .join(Biospecimen.participant)
                 .filter(Participant.study_id == study_id)
                 .group_by(ReadGroup.kf_id))

        # Filter by genomic_file_id
        if genomic_file_id:
            q = (q.join(ReadGroupGenomicFile,
                        ReadGroup.kf_id == ReadGroupGenomicFile.read_group_id)
                 .filter(ReadGroupGenomicFile.genomic_file_id ==
                         genomic_file_id))

        return (ReadGroupSchema(many=True)
                .jsonify(Pagination(q, after, limit)))

    def post(self):
        """
        Create a new read_group
        ---
        template:
          path:
            new_resource.yml
          properties:
            resource:
              ReadGroup
        """

        body = request.get_json(force=True)

        # Deserialize
        try:
            rg = ReadGroupSchema(strict=True).load(body).data
        # Request body not valid
        except ValidationError as e:
            abort(400, 'could not create read_group: {}'
                  .format(e.messages))

        # Add to and save in database
        db.session.add(rg)
        db.session.commit()

        return ReadGroupSchema(201,
                               'read_group {} created'
                               .format(rg.kf_id)).jsonify(rg), 201


class ReadGroupAPI(CRUDView):
    """
    ReadGroup REST API
    """
    endpoint = 'read_groups'
    rule = '/read-groups/<string:kf_id>'
    schemas = {'ReadGroup': ReadGroupSchema}

    def get(self, kf_id):
        """
        Get a read_group by id
        ---
        template:
          path:
            get_by_id.yml
          properties:
            resource:
              ReadGroup
        """
        # Get one
        rg = ReadGroup.query.get(kf_id)
        if rg is None:
            abort(404, 'could not find {} `{}`'
                  .format('read_group', kf_id))
        return ReadGroupSchema().jsonify(rg)

    def patch(self, kf_id):
        """
        Update an existing read_group.

        Allows partial update of resource
        ---
        template:
          path:
            update_by_id.yml
          properties:
            resource:
              ReadGroup
        """
        rg = ReadGroup.query.get(kf_id)
        if rg is None:
            abort(404, 'could not find {} `{}`'
                  .format('read_group', kf_id))

        # Partial update - validate but allow missing required fields
        body = request.get_json(force=True) or {}
        try:
            rg = (ReadGroupSchema(strict=True).
                  load(body, instance=rg,
                       partial=True).data)
        except ValidationError as err:
            abort(400, 'could not update read_group: {}'
                  .format(err.messages))

        db.session.add(rg)
        db.session.commit()

        return ReadGroupSchema(
            200, 'read_group {} updated'.format(rg.kf_id)
        ).jsonify(rg), 200

    def delete(self, kf_id):
        """
        Delete read_group by id

        Deletes a read_group given a Kids First id
        ---
        template:
          path:
            delete_by_id.yml
          properties:
            resource:
              ReadGroup
        """

        # Check if read_group exists
        rg = ReadGroup.query.get(kf_id)
        if rg is None:
            abort(404, 'could not find {} `{}`'
                  .format('read_group', kf_id))

        # Save in database
        db.session.delete(rg)
        db.session.commit()

        return ReadGroupSchema(200,
                               'read_group {} deleted'
                               .format(rg.kf_id)).jsonify(rg), 200
