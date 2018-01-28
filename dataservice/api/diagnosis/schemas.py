from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.common.schemas import BaseSchema
from marshmallow_sqlalchemy import field_for
from marshmallow import validates, ValidationError
from dataservice.extensions import ma

MIN_AGE_DAYS = 0
MAX_AGE_DAYS = 32872


class DiagnosisSchema(BaseSchema):
    # Should not have to do this, since participant_id is part of the
    # Diagnosis model and should be dumped. However it looks like this is
    # still a bug in marshmallow_sqlalchemy. The bug is that ma sets
    # dump_only=True for foreign keys by default. See link below
    # https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/20
    participant_id = field_for(Diagnosis, 'participant_id', required=True,
                               load_only=True)

    class Meta(BaseSchema.Meta):
        model = Diagnosis

    @validates('age_at_event_days')
    def validate_age(self, value):
        if value < MIN_AGE_DAYS:
            raise ValidationError('Age must be an integer greater than {}.'
                                  .format(MIN_AGE_DAYS))
        if value > MAX_AGE_DAYS:
            raise ValidationError('Age must be an integer less than {}.'
                                  .format(MAX_AGE_DAYS))

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.diagnoses', kf_id='<kf_id>'),
        'collection': ma.URLFor('api.diagnoses'),
        'participant': ma.URLFor('api.participants', kf_id='<participant_id>')
    })
