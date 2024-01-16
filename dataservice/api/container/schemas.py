from marshmallow_sqlalchemy import field_for

from dataservice.extensions import ma
from dataservice.api.container.models import Container
from dataservice.api.common.schemas import BaseSchema


class ContainerSchema(BaseSchema):
    biospecimen_id = field_for(Container, 'biospecimen_id', required=True,
                               load_only=True)
    sample_id = field_for(Container, 'sample_id', required=True,
                               load_only=True)

    class Meta(BaseSchema.Meta):
        model = Container
        resource_url = 'api.containers'
        collection_url = 'api.containers_list'
        exclude = (BaseSchema.Meta.exclude +
                   ('biospecimen', ))

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'biospecimen': ma.URLFor('api.biospecimens', kf_id='<biospecimen_id>'),
        'sample': ma.URLFor('api.samples', kf_id='<sample_id>'),
    })
