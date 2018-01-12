from sqlalchemy.ext.declarative import declared_attr

from datetime import datetime
from . import db

from .id_service import assign_id


class IDMixin:
    """
    Defines base ID columns common on all Kids First tables
    """
    _id = db.Column(db.Integer(), primary_key=True)
    kf_id = db.Column(db.String(32), unique=True, default=assign_id())
    uuid = db.Column(db.String(32), unique=True, default=assign_id())


class TimestampMixin:
    """
    Defines the common timestammp columns on all Kids First tables
    """
    created_at = db.Column(db.DateTime(), default=datetime.now())
    modified_at = db.Column(db.DateTime(), default=datetime.now())


class HasFileMixin:
    @declared_attr
    def file_id(cls):
        return db.Column('file_id', db.ForeignKey('file._id'))

    @declared_attr
    def files(cls):
        return db.relationship("File")


class Base(db.Model, IDMixin, TimestampMixin):
    """
    Defines base SQlAlchemy model class
    """
    pass


class File(Base):
    """
    Defines a file
    """
    __tablename__ = "file"
    name = db.Column(db.String(32))
    data_type = db.Column(db.String(32))
    size = db.Column(db.Integer(), default=0)


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
