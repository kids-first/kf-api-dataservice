from marshmallow_sqlalchemy import field_for

from dataservice.api.sample.models import Sample
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_age
from dataservice.extensions import ma


class SampleSchema(BaseSchema):
    # Should not have to do this, since participant_id is part of the
    # Sample model and should be dumped. However it looks like this is
    # still a bug in marshmallow_sqlalchemy. The bug is that ma sets
    # dump_only=True for foreign keys by default. See link below
    # https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/20
    participant_id = field_for(Sample, 'participant_id', required=True,
                               load_only=True)
    age_at_event_days = field_for(Sample, 'age_at_event_days',
                                  validate=validate_age)

    class Meta(BaseSchema.Meta):
        model = Sample

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.samples', kf_id='<kf_id>'),
        'collection': ma.URLFor('api.samples'),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
