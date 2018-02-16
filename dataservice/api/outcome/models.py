from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class Outcome(db.Model, Base):
    """
    Outcome entity.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param vital_status: Vital status of the participant
    :param disease_related: true if Dead and cause of death was disease related
    , false if Dead and cause of death was disease related, Not Reported
    :param age_at_event_days: Age at the time of outcome occured
    in number of days since birth.
    """
    __tablename__ = 'outcome'
    __prefix__ = 'OC'

    vital_status = db.Column(db.Text())
    disease_related = db.Column(db.Text())
    age_at_event_days = db.Column(db.Integer())
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False)
