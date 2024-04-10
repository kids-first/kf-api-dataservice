from marshmallow_sqlalchemy import field_for

from dataservice.api.study.models import Study
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.extensions import ma
from dataservice.api.common.validation import enum_validation_generator
from marshmallow import ValidationError

RELEASE_STATUS_ENUM = {'Pending', 'Waiting', 'Running', 'Staged',
                       'Publishing', 'Published', 'Failed', 'Canceled'}


def validate_parent_study_id(value):
    study = Study.query.get(value)
    if not study:
        raise ValidationError(
            f"Parent study {value} does not exist"
        )


class StudySchema(BaseSchema):

    investigator_id = field_for(Study, 'investigator_id',
                                required=False, load_only=True,
                                example='IG_ABB2C104')

    parent_study_id = field_for(
        Study, 'parent_study_id', example='SD_ABB2C104',
        validate=validate_parent_study_id
    )

    release_status = field_for(Study, 'release_status',
                               validate=enum_validation_generator(
                                   RELEASE_STATUS_ENUM))

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
