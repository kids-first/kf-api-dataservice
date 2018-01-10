from datetime import datetime
from . import db

from .id_service import assign_id


class Person(db.Model):
    """
    Person entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param source_name: Name given to person by contributor
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = "person"
    _id = db.Column(db.Integer(), primary_key=True)
    kf_id = db.Column(db.String(32), unique=True, default=assign_id())
    source_name = db.Column(db.String(32))
    created_at = db.Column(db.DateTime(), default=datetime.now())
    modified_at = db.Column(db.DateTime(), default=datetime.now())
