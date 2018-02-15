from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.participant.models import Participant


class Study(db.Model, Base):
    """
    Study entity representing the dbGap study.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param data_access_authority: Name of organization which governs data
    access
    :param external_id: dbGap accession number
    :param version: dbGap version
    :param name: Name or title of study
    :param attribution: Link to attribution prose provided by dbGap
    """
    __tablename__ = "study"

    data_access_authority = db.Column(db.Text(),
                                      nullable=False,
                                      default='dbGap')

    external_id = db.Column(db.Text(), nullable=False)
    version = db.Column(db.Text())
    name = db.Column(db.Text())
    attribution = db.Column(db.Text())

    participants = db.relationship(Participant,
                                   cascade="all, delete-orphan",
                                   backref='study')

    def __repr__(self):
        return '<Study {}>'.format(self.external_id)
