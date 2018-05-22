from marshmallow_sqlalchemy import field_for

from dataservice.api.study.models import Study
from dataservice.api.common.schemas import BaseSchema, COMMON_ENUM
from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.extensions import ma
from dataservice.api.common.validation import enum_validation_generator
from marshmallow import post_dump

RELEASE_STATUS_ENUM = {'pending': 'Pending', 'waiting': 'Waiting',
                       'running': 'Running', 'staged': 'Staged',
                       'publishing': 'Publishing', 'published': 'Published',
                       'failed': 'Failed', 'canceled': 'Canceled'}
RELEASE_STATUS_ENUM.update(COMMON_ENUM)


class StudySchema(BaseSchema):

    investigator_id = field_for(Study, 'investigator_id',
                                required=False, load_only=True,
                                example='IG_ABB2C104')

    release_status = field_for(Study, 'release_status',
                               validate=enum_validation_generator(
                                   RELEASE_STATUS_ENUM))

    @post_dump()
    def auto_populate_enum(self, data):
        if data['release_status'] is not None:
            data['release_status'] = RELEASE_STATUS_ENUM[
                data['release_status'].lower()]

    class Meta(BaseSchema.Meta):
        model = Study
        resource_url = 'api.studies'
        collection_url = 'api.studies_list'
        exclude = BaseSchema.Meta.exclude + ('participants', 'study_files')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'investigator': PatchedURLFor('api.investigators',
                                      kf_id='<investigator_id>'),
        'participants': ma.URLFor('api.participants_list', study_id='<kf_id>'),
        'study_files': ma.URLFor('api.study_files_list', study_id='<kf_id>')
    })
