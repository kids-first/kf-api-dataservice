from dataservice.api.demographic.models import Demographic
from dataservice.api.common.schemas import BaseSchema
from marshmallow_sqlalchemy import field_for
from dataservice.extensions import ma


class DemographicSchema(BaseSchema):
    # Should not have to do this, since participant_id is part of the
    # Demographic model and should be dumped. However it looks like this is
    # still a bug in marshmallow_sqlalchemy. The bug is that ma sets
    # dump_only=True for foreign keys by default. See link below
    # https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/20
    participant_id = field_for(Demographic, 'participant_id', required=True,
                               load_only=True)

    class Meta(BaseSchema.Meta):
        resource_url = 'api.demographics'
        collection_url = 'api.demographics_list'
        model = Demographic

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
