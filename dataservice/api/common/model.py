from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr

from dataservice.extensions import db
from dataservice.api.common.id_service import uuid_generator, kf_id_generator


class IDMixin:
    """
    Defines base ID columns common on all Kids First tables
    """
    _id = db.Column(db.Integer(), primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=uuid_generator)
    kf_id = db.Column(db.String(8), unique=True, default=kf_id_generator)


class TimestampMixin:
    """
    Defines the common timestammp columns on all Kids First tables
    """
    created_at = db.Column(db.DateTime(), default=datetime.now)
    modified_at = db.Column(db.DateTime(), default=datetime.now)


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
