from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from enum import Enum


class Outcome(db.Model, Base):
    """
    Outcome entity.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to outcome by contributor
    :param vital_status: Vital status of the participant
    :param disease_related: true if Dead and cause of death was disease related
    , false if Dead and cause of death was disease related, Not Reported
    :param age_at_event_days: Age at the time of outcome occured
    in number of days since birth.
    """
    __tablename__ = 'outcome'
    __prefix__ = 'OC'

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    vital_status = db.Column(db.Text(),
                             doc='The vital status reported')
    disease_related = db.Column(db.Text())
    age_at_event_days = db.Column(db.Integer(),
                                  doc='Age at the time of event occurred in '
                                      'number of days since birth.')
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False,
                               doc='kf_id of the participant this outcome was '
                                   'reported for')


class VitalStatusEnum(Enum):

    """
     Enum class for vital_status field with possible choices
    """
    Alive = "Alive"
    Dead = "Dead"
    Not_Reported = "Not Reported"
    Not_Applicable = "Not Applicable"
    Not_Allowed_To_Collect = "Not Allowed To Collect"
    Not_Available = "Not Available"


class DiseaseRelatedEnum(Enum):

    """
     Enum class for disease_related field with possible choices
    """
    Yes = "Yes"
    No = "No"
    Not_Reported = "Not Reported"
    Not_Applicable = "Not Applicable"
    Not_Allowed_To_Collect = "Not Allowed To Collect"
    Not_Available = "Not Available"
