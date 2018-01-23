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
    """
    __tablename__ = "sample"
    external_id = db.Column(db.String(32))
    tissue_type = db.Column(db.String(32))
    composition = db.Column(db.String(32))
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.kf_id'),
                               nullable=False)
