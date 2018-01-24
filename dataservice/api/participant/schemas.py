from dataservice.api.participant.models import Participant
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma
from marshmallow_sqlalchemy import field_for


class ParticipantSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = Participant
        dump_only = ('created_at', 'modified_at')

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.participants', kf_id='<kf_id>')
    })
