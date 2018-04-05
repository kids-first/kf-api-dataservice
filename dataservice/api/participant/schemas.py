from marshmallow_sqlalchemy import field_for

from dataservice.api.participant.models import Participant
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class ParticipantSchema(BaseSchema):
    study_id = field_for(Participant, 'study_id', required=True,
                         load_only=True)
    family_id = field_for(Participant, 'family_id',
                          required=False,
                          load_only=True, example='FM_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = Participant
        resource_url = 'api.participants'
        collection_url = 'api.participants_list'
        exclude = BaseSchema.Meta.exclude + ('study', 'family')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'study': ma.URLFor('api.studies', kf_id='<study_id>'),
    })

    def dump(self, p, *args, **kwargs):
        """
        Check if there is a family_id present on the participant and insert
        a link if there is before dumping, then remove link after the dump
        """
        if kwargs['many'] is False and p.family_id is not None:
            self.fields['_links'].schema['family'] = (
                ma.URLFor('api.families', kf_id='<family_id>')
            )
            data = super(ParticipantSchema, self).dump(p, *args, **kwargs)
            del self.fields['_links'].schema['family']
            return data
        return super(ParticipantSchema, self).dump(p, *args, **kwargs)
