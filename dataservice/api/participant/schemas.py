from marshmallow_sqlalchemy import field_for

from dataservice.api.participant.models import Participant
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class ParticipantSchema(BaseSchema):
    study_id = field_for(Participant, 'study_id', required=True,
                         load_only=True)
    family_id = field_for(Participant, 'family_id',
                          required=False, example='FM_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = Participant
        resource_url = 'api.participants'
        collection_url = 'api.participants_list'
        exclude = BaseSchema.Meta.exclude + ('study', 'family')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'study': ma.URLFor('api.studies', kf_id='<study_id>')
    })

    def dump(self, obj, *args, **kwargs):
        """
        Modify schema dump to render nullable foreign keys as hyperlinks

        For non-null foreign keys render as hyperlink in _links
        For null foreign keys render as null in _links

        Example after rendering links:
        '_links': {
            'self': /participants/PT_00001111,
            'collection': /participants
            'family': null,
            'study': /studies/ST_00001111
        }
        """

        marshal_result = super().dump(obj, *args, **kwargs)

        self.render_nullable_fk_as_link('family_id',
                                        'api.families',
                                        marshal_result.data)

        return marshal_result
