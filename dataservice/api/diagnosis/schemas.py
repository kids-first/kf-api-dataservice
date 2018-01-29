from marshmallow_sqlalchemy import field_for
from marshmallow import validates, ValidationError

from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.validation import validate_age
from dataservice.extensions import ma


class DiagnosisSchema(BaseSchema):
    # Should not have to do this, since participant_id is part of the
    # Diagnosis model and should be dumped. However it looks like this is
    # still a bug in marshmallow_sqlalchemy. The bug is that ma sets
    # dump_only=True for foreign keys by default. See link below
    # https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/20
    participant_id = field_for(Diagnosis, 'participant_id', required=True,
                               load_only=True)
    age_at_event_days = field_for(Diagnosis, 'age_at_event_days',
                                  validate=validate_age)

    class Meta(BaseSchema.Meta):
        model = Diagnosis

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.diagnoses', kf_id='<kf_id>'),
        'collection': ma.URLFor('api.diagnoses'),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
