from marshmallow_sqlalchemy import field_for

from dataservice.api.participant.models import Participant
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class ParticipantSchema(BaseSchema):
    # Should not have to do this, since participant_id is part of the
    # Demographic model and should be dumped. However it looks like this is
    # still a bug in marshmallow_sqlalchemy. The bug is that ma sets
    # dump_only=True for foreign keys by default. See link below
    # https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/20
    study_id = field_for(Participant, 'study_id', required=True,
                         load_only=True)

    class Meta(BaseSchema.Meta):
        model = Participant

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.participants', kf_id='<kf_id>')
    }, description='Resource links and pagination')
