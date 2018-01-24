from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.demographic.models import Demographic


class Participant(db.Model, Base):
    """
    Participant entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to participant by contributor
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = "participant"
    external_id = db.Column(db.String(32))
    demographic = db.relationship(Demographic, backref='participant',
                                  uselist=False, cascade="all, delete-orphan",
                                  lazy='joined')
