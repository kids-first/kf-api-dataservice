from dataservice.extensions import db
from dataservice.api.common.model import Base


class Diagnosis(db.Model, Base):
    """
    Diagnosis entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to diagnosis by contributor
    :param primary_diagnosis: Diagnosis of the participant
    :param progression_or_recurence: yes/no/unknown indicator to identify
     whether a patient has had a new event after initial treatment.
    :param age_at_event_days: Days since participant date of birth at the
    time of diagnosis event.
    """

    __tablename__ = 'diagnosis'
    external_id = db.Column(db.Text())
    diagnosis = db.Column(db.Text())
    progression_or_recurrence = db.Column(db.Text())
    age_at_event_days = db.Column(db.Integer())
    participant_id = db.Column(db.String(8),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False)
