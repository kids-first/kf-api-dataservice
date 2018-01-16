from dataservice import db
from dataservice.api.common.model import Base


class Person(Base):
    """
    Person entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to person by contributor
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = "person"
    external_id = db.Column(db.String(32))
