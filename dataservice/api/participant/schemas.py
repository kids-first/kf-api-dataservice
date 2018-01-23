from dataservice.api.participant.models import Participant
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class ParticipantSchema(BaseSchema):
    class Meta:
        model = Participant
        fields = ('kf_id', 'external_id', '_links')

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.participants', kf_id='<kf_id>')
    })
