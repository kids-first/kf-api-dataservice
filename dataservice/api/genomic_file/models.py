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

    :param kf_id: Unique id given by the Kid's First DCC
    :param uuid: The baseid assigned to the file by indexd
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param file_name: Name of file
    :param data_type: Type of genomic file (i.e. aligned reads)
    :param file_format: Format of file
    :param file_size: Size of file in bytes
    :param file_url: Location of file
    :param md5sum: 128 bit md5 hash of file
    :param controlled_access: Whether or not the file is controlled access
    :param is_harmonized: Whether or not the file is harmonized
    :param reference_genome: Original reference genome of the
     unharmonized genomic files
    """
    __tablename__ = 'genomic_file'
    __prefix__ = 'GF'

    file_name = db.Column(db.Text(), doc='Name of file')
    data_type = db.Column(db.Text(), doc='Type of genomic file')
    file_format = db.Column(db.Text(), doc='Size of file in bytes')
    file_size = db.Column(db.BigInteger(), doc='Size of file in bytes')
    file_url = db.Column(db.Text(), doc='Location of file')
    is_harmonized = db.Column(db.Boolean(), doc='Whether or not the file'
                              ' is harmonized')
    reference_genome = db.Column(db.Text(), doc='Original reference genome of'
                                 ' the unharmonized genomic files')
    # See link for why md5sum should use uuid type
    # https://dba.stackexchange.com/questions/115271/what-is-the-optimal-data-type-for-an-md5-field
    md5sum = db.Column(UUID(), unique=True, doc='128 bit md5 hash of file')
    controlled_access = db.Column(db.Boolean(), doc='Whether or not the file'
                                  'is controlled access')
    sequencing_experiment_id = db.Column(KfId(),
                                         db.ForeignKey(
                                         'sequencing_experiment.kf_id'),
                                         nullable=False)
    biospecimen_id = db.Column(KfId(), db.ForeignKey('biospecimen.kf_id'),
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
