from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class SequencingCenterSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        resource_url = 'api.sequencing_centers'
        collection_url = 'api.sequencing_centers_list'
        model = SequencingCenter
        exclude = BaseSchema.Meta.exclude + ('biospecimens',
                                             'sequencing_experiments',)

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'biospecimens': ma.URLFor('api.biospecimens_list',
                                  sequencing_center_id='<kf_id>'),
        'sequencing_experiments': ma.URLFor('api.sequencing_experiments_list',
                                            sequencing_center_id='<kf_id>')

    }, description='Resource links and pagination')
