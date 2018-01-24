from dataservice.extensions import db
from dataservice.api.common.model import Base


class Sample(db.Model, Base):
    """
    Sample entity.
    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sample by contributor
    :param composition : composition of the sample
    :param tissue_type: Either Normal or Tumor
    :param anatomical_site : location of the collected sample
    :param age_at_event_days: age of participant when sample was collected
    """
    __tablename__ = "sample"
    external_id = db.Column(db.Text())
    tissue_type = db.Column(db.Text())
    composition = db.Column(db.Text())
    anatomical_site = db.Column(db.Text())
    age_at_event_days = db.Column(db.Integer())
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.kf_id'),
                               nullable=False)
