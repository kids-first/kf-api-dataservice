from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class Phenotype(db.Model, Base):
    """
    Phenotype entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param phenotype: Name given to Phenotype by contributor
    :param hpo_id: hpo id
    :param observed: whether phenotype is negative or positive
    :param age_at_event_days: Age at the time phenotype was
            observed, expressed in number of days since birth
    """
    __tablename__ = 'phenotype'
    __prefix__ = 'PH'

    phenotype = db.Column(db.Text())
    hpo_id = db.Column(db.Text())
    observed = db.Column(db.Text())
    age_at_event_days = db.Column(db.Integer())
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False)
