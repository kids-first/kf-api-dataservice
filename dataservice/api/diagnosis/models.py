from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class Diagnosis(db.Model, Base):
    """
    Diagnosis entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to diagnosis by contributor
    :param diagnosis: Diagnosis of the participant
    :param diagnosis_category: High level diagnosis categorization
    :param tumor_location: Location of the tumor
    :param age_at_event_days: Age at the time of diagnosis expressed
    in number of days since birth.
    """
    __tablename__ = 'diagnosis'
    __prefix__ = 'DG'

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    diagnosis = db.Column(db.Text(),
                          doc='the pathological diagnosis')
    diagnosis_category = db.Column(db.Text(),
                                   doc='High level diagnosis categorization'
                                   )
    tumor_location = db.Column(db.Text(),
                               doc='location of the tumor')
    age_at_event_days = db.Column(db.Integer(),
                                  doc='age when diagnosis was made')
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               doc='the participant who was diagnosed',
                               nullable=False)
