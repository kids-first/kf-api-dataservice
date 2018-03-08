from dataservice.api.study.models import Study
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class StudySchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = Study
        resource_url = 'api.studies'
        collection_url = 'api.studies_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url)
    })
