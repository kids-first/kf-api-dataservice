from marshmallow_sqlalchemy import field_for

from dataservice.api.study_file.models import StudyFile
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class StudyFileSchema(BaseSchema):
    study_id = field_for(StudyFile, 'study_id', required=True,
                         load_only=True)

    class Meta(BaseSchema.Meta):
        model = StudyFile
        resource_url = 'api.study_files'
        collection_url = 'api.study_files_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'study_files': ma.URLFor('api.studies', kf_id='<study_id>')
    })
