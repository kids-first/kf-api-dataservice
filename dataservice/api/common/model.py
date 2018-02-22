from datetime import datetime
import sqlalchemy.types as types
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID

from dataservice.extensions import db
from dataservice.api.common.id_service import uuid_generator, kf_id_generator


class KfId(types.TypeDecorator):
    """
    A kids first id type
    """
    impl = types.String

    def __init__(self, *args, **kwargs):
        kwargs['length'] = 11
        super(KfId, self).__init__(*args, **kwargs)


class IDMixin:
    """
    Defines base ID columns common on all Kids First tables
    """
    __prefix__ = '__'

    @declared_attr
    def kf_id(cls):
        kf_id = db.Column(KfId(), primary_key=True,
                          doc="ID assigned by Kids First",
                          default=kf_id_generator(cls.__prefix__))
        return kf_id

    uuid = db.Column(UUID(), unique=True, default=uuid_generator)


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
