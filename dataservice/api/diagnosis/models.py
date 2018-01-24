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
    :param days_to_last_followup: Time interval from the date of last follow up
     to the date of initial pathologic diagnosis, represented as a calculated
     number of days.
    """

    __tablename__ = 'diagnosis'
    external_id = db.Column(db.String(32))
    primary_diagnosis = db.Column(db.Text)
    progression_or_recurence = db.Column(db.String(32))
    days_to_last_followup = db.Column(db.Integer())
