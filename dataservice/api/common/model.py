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


class Base(IDMixin, TimestampMixin):
    """
    Defines base SQlAlchemy model class
    """
    pass
