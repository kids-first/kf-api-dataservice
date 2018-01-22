from flask_restplus import fields

from dataservice.api.common.serializers import (
    base_entity,
    base_response,
    base_pagination,
    _status_fields,
    _paginate_fields
)
from dataservice.api.participant.resources import participant_api


participant_api.models['Status'] = _status_fields
participant_api.models['PaginateFields'] = _paginate_fields

# Fields unique to a Participant, used as the new participant request model
participant_fields = participant_api.model('ParticipantFields', {
    'external_id': fields.String(
        example='SUBJ-3993',
        description='Identifier used in the original study data')
})

participant_model = participant_api.clone('Participant', base_entity,
                                          participant_fields)

participant_list = participant_api.clone("ParticipantsList", base_pagination, {
    "results": fields.List(fields.Nested(participant_model))
})

participant_response = participant_api.clone('ParticipantResponse',
                                             base_response, {
                                                 'results': fields.Nested(
                                                     participant_model)
                                             })
