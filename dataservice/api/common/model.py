from datetime import datetime

from dataservice.extensions import db
from dataservice.api.common.id_service import uuid_generator, kf_id_generator


class IDMixin:
    """
    Defines base ID columns common on all Kids First tables
    """
    uuid = db.Column(db.String(36), unique=True, default=uuid_generator)
    kf_id = db.Column(db.String(8), primary_key=True,
                      doc="ID assigned by Kids First", default=kf_id_generator)


class TimestampMixin:
    """
    Defines the common timestammp columns on all Kids First tables
    """
    created_at = db.Column(db.DateTime(), default=datetime.now,
                           doc="Time of object creation")
    modified_at = db.Column(db.DateTime(), default=datetime.now,
                            doc="Time of last modification")


class Base(IDMixin, TimestampMixin):
    """
    Defines base SQlAlchemy model class
    """
    pass
