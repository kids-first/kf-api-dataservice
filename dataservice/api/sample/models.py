from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.aliquot.models import Aliquot


class Sample(db.Model, Base):
    """
    Sample entity.
    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sample by contributor
    :param composition : The cellular composition of the sample.
    :param tissue_type: description of the kind of tissue collected
           with respect to disease status or proximity to tumor tissue
    :param anatomical_site : The name of the primary disease site of the
           submitted tumor sample
    :param age_at_event_days: age of participant when sample was collected
    :param tumor_descriptor: The kind of disease present in the tumor
           specimen as related to a specific timepoint
    """
    __tablename__ = "sample"
    external_id = db.Column(db.Text())
    tissue_type = db.Column(db.Text())
    composition = db.Column(db.Text())
    anatomical_site = db.Column(db.Text())
    age_at_event_days = db.Column(db.Integer())
    tumor_descriptor = db.Column(db.Text())
    aliquots = db.relationship(Aliquot, back_populates='samples',
                               cascade="all, delete-orphan")
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.kf_id'),
                               nullable=False)
