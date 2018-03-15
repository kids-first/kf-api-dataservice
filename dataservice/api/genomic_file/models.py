import requests

from flask import abort, current_app
from requests.exceptions import HTTPError
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID

from dataservice.extensions import db, indexd
from dataservice.api.common.model import Base, KfId


class GenomicFile(db.Model, Base):
    """
    GenomicFile entity.

    A GenomicFile has fields that are stored in both the datamodel, and in
    the Gen3 indexd service. The two are linked through a common uuid.

    ## Lifetime

    ### Creation

    When a genomic file is created, an instance of the orm model here is
    created, and when persisted to the database, a request is sent to Gen3
    indexd to register the file in the service. Upon successful registry
    of the file, a response containing a did (digital identifier) will be
    recieved. The GenomicFile will then be inserted into the database using
    the did as its uuid.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param uuid: UUID assigned to file from Gen3
    :param file_name: Name of file
    :param data_type: Type of genomic file (i.e. aligned reads)
    :param file_format: Format of file
    :param file_size: Size of file in bytes
    :param file_url: Location of file
    :param md5sum: 128 bit md5 hash of file
    :param controlled_access: whether or not the file is controlled access
    """
    __tablename__ = 'genomic_file'
    __prefix__ = 'GF'

    file_name = db.Column(db.Text())
    data_type = db.Column(db.Text())
    file_format = db.Column(db.Text())
    file_size = db.Column(db.BigInteger())
    file_url = db.Column(db.Text())
    md5sum = db.Column(UUID(as_uuid=True), unique=True)
    controlled_access = db.Column(db.Boolean())
    sequencing_experiment_id = db.Column(KfId(),
                                         db.ForeignKey(
                                         'sequencing_experiment.kf_id'),
                                         nullable=False)

    # Fields used by indexd, but not tracked in the database
    urls = []
    rev = None
    hashes = {}
    # The metadata property is already used by sqlalchemy
    _metadata = {}
    size = None

    def merge_indexd(self):
        """
        Gets additional fields from indexd
        """
        resp = indexd.get(self.uuid)

        # Might want to use partial deserialization here
        for prop, v in resp.json().items():
            if hasattr(self, prop):
                setattr(self, prop, v)

        if 'metadata' in resp.json():
            self._metadata = resp.json()['metadata']


@event.listens_for(GenomicFile, 'before_insert')
def register_indexd(mapper, connection, target):
    """
    Registers the genomic file with indexd.
    The response upon successful registry will contain a `did` which will
    be used as the target's uuid so that it may be joined with the indexd
    data.
    """
    if current_app.config['INDEXD_URL'] is None:
        return

    resp = indexd.new(target)
    # Update the target's uuid with the new did recieved from indexd
    target.uuid = resp['did']
    return target


@event.listens_for(GenomicFile, 'before_update')
def update_indexd(mapper, connection, target):
    """
    Updates a document in indexd
    """
    indexd.update(target)


@event.listens_for(GenomicFile, 'before_delete')
def delete_indexd(mapper, connection, target):
    """
    Deletes a document in indexd
    """
    # Get the current revision if not already loaded
    if target.rev is None:
        target.merge_indexd()

    indexd.delete(target)
