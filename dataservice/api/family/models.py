from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.participant.models import Participant


class Family(db.Model, Base):
    """
    Family entity.

    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to the family by contributor
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = "family"
    __prefix__ = 'FM'

    external_id = db.Column(db.Text(), doc='ID used by external study')

    participants = db.relationship(Participant, backref='family')
