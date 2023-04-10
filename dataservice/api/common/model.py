from datetime import datetime
from flask import abort, current_app
from requests.exceptions import HTTPError
import sqlalchemy.types as types
from sqlalchemy import event, inspect
from sqlalchemy.orm import reconstructor
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID

from dataservice.extensions import db, indexd
from dataservice.extensions.flask_indexd import RecordNotFound
from dataservice.api.common.id_service import uuid_generator, kf_id_generator

COMMON_ENUM = {"Not Reported", "Not Applicable", "Not Allowed To Collect",
               "Not Available", "Reported Unknown"}

VISIBILITY_REASON_ENUM = {
    "Ready For Release", "Pre-Release", "Peddy Issue", "Consent Hold",
    "File Quality Issue", "Other", "Unknown"
}


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


class IndexdFile:
    """
    Field reflection for objects that are stored in indexd

    # Creation

    When an indexd file is created, an instance of the orm model here is
    created, and when persisted to the database, a request is sent to Gen3
    indexd to register the file in the service. Upon successful registry
    of the file, a response containing a did (digital identifier) will be
    recieved. The IndexdFile will then be inserted into the database using
    the baseid as its uuid.

    # Update

    When a file is updated in indexd, a new version with a new did is created.
    The document still shares a base_id with the older versions, but a document
    may not be retrieved with the base_id alone. Because of this, the
    latest_did is stored on the file.

    # Deletion

    A file deleted through a DELETE on the dataservice api will immediately
    delete that file from the dataservice's database, as well as send
    a corresponding DELETE to the indexd service.
    Though it should not occur, a file deleted through indexd will remain
    in the dataservice's database until it a retrieval is attempted.
    If indexd returns a not found error, the dataservice will automatically
    remove that file from the database, giving the appearence that the two
    are in sync from the viewpoint of the dataservice API.
    """
    # Store the latest did in the database
    # files in indexd cannot be looked up by their baseid
    latest_did = db.Column(UUID(), nullable=False)

    file_name = ''
    urls = []
    rev = None
    hashes = {}
    acl = []
    # The metadata property is already used by sqlalchemy
    _metadata = {}
    size = None

    @reconstructor
    def constructor(self):
        """
        Builds the object by initializing properties and updating them
        from indexd.

        """
        # Fields used by indexd, but not tracked in the database
        self.file_name = ''
        self.urls = []
        self.rev = None
        self.hashes = {}
        self.acl = []
        # The metadata property is already used by sqlalchemy
        self._metadata = {}
        self.size = None
        # Update fields from indexd
        self.merge_indexd()

    @property
    def access_urls(self):
        """
        Access urls should contain only links out to gen3 data endpoints
        that are used to download the files themselves.

        For urls that are already https:// urls, we will consider them as
        valid gen3 locations, for urls that are s3:// protocol, we will assume
        that they are internal files and resolve them to our gen3 service
        """
        urls = []
        for url in self.urls:
            if url.startswith('s3://'):
                url = (f'{current_app.config["GEN3_URL"]}'
                       f'/data/{self.latest_did}')
            urls.append(url)

        return urls

    def merge_indexd(self):
        """
        If the document matching this object's latest_did cannot be found in
        indexd, remove the object from the database

        :returns: This object, if merge was successful, otherwise None
        """
        try:
            return indexd.get(self)
        except RecordNotFound as err:
            self.was_deleted = True
            db.session.delete(self)
            db.session.commit()
            return None


@event.listens_for(IndexdFile, 'before_insert', propagate=True)
def register_indexd(mapper, connection, target):
    """
    Registers the genomic file with indexd.
    The response upon successful registry will contain a `did` which will
    be used as the target's uuid so that it may be joined with the indexd
    data.
    """
    return indexd.new(target)


@event.listens_for(IndexdFile, 'before_update', propagate=True)
def update_indexd(mapper, connection, target):
    """
    Updates a document in indexd
    """
    try:
        return indexd.update(target)
    except RecordNotFound:
        target.was_deleted = True
        db.session.delete(target)
        db.session.commit()
        return None
    except HTTPError as err:
        abort(500, 'could not update the file: ' + str(err))


@event.listens_for(IndexdFile, 'before_delete', propagate=True)
def delete_indexd(mapper, connection, target):
    """
    Deletes a document in indexd
    """
    if (hasattr(target, 'was_deleted') and
            target.was_deleted):
        return

    # Get the current revision if not already loaded
    if target.rev is None:
        target.merge_indexd()

    indexd.delete(target)


class TimestampMixin:
    """
    Defines the common timestammp columns on all Kids First tables
    """
    created_at = db.Column(db.DateTime(), default=datetime.now, index=True,
                           doc="Time of object creation")
    modified_at = db.Column(db.DateTime(), default=datetime.now,
                            onupdate=datetime.now,
                            doc="Time of last modification")


class Base(IDMixin, TimestampMixin):
    """
    Defines base SQlAlchemy model class
    :param visible: Flags visibility of data from the dataservice
    """
    visible = db.Column(db.Boolean(),
                        nullable=False,
                        server_default='true',
                        doc='Flags visibility of data from the dataservice')
    visibility_reason = db.Column(
        db.Text(),
        doc='Gives justification for the value in the visible column'
    )
    visibility_comment = db.Column(
        db.Text(),
        doc='Additional details for the visibility reason'
    )
