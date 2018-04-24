from marshmallow_sqlalchemy import field_for

from dataservice.api.study.models import Study
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class StudySchema(BaseSchema):

    investigator_id = field_for(Study, 'investigator_id',
                                required=False, example='IG_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = Study
        resource_url = 'api.studies'
        collection_url = 'api.studies_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url)
    })

    # def dump(self, obj, *args, **kwargs):
    #     """
    #     Modify schema dump to render nullable foreign keys as hyperlinks
    #
    #     For non-null foreign keys render as hyperlink in _links
    #     For null foreign keys render as null in _links
    #
    #     Example after rendering links:
    #     '_links': {
    #         'self': /studies/ST_00001111,
    #         'collection': /studies
    #         'investigator': null,
    #         'study': /studies/ST_00001111
    #     }
    #     """
    #
    #     marshal_result = super().dump(obj, *args, **kwargs)
    #
    #     self.render_nullable_fk_as_link('investigator_id',
    #                                     'api.investigators',
    #                                     marshal_result.data)
    #
    #     return marshal_result
