from sqlalchemy.dialects.postgresql import UUID
from dataservice.extensions import db
from dataservice.api.common.model import Base, IndexdFile, KfId


class GenomicFile(db.Model, Base, IndexdFile):
    """
    GenomicFile entity.

    A GenomicFile has fields that are stored in both the datamodel, and in
    the Gen3 indexd service. The two are linked through a common uuid.


    :param kf_id: Unique id given by the Kid's First DCC
    :param uuid: The baseid assigned to the file by indexd
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param file_name: Name of file
    :param data_type: Type of genomic file (i.e. aligned reads)
    :param file_format: Format of file
    :param controlled_access: Whether or not the file is controlled access
    :param is_harmonized: Whether or not the file is harmonized
    :param reference_genome: Original reference genome of the
     unharmonized genomic files
    :param latest_did: UUID for the latest version of the file in indexd
    :param urls: Locations of file
    :param hashes: A dict keyed by hash type containing hashes of the file
    :param _metadata: A dict with any additional information
    :param controlled_access: whether or not the file is controlled access
    """
    __tablename__ = 'genomic_file'
    __prefix__ = 'GF'

    data_type = db.Column(db.Text(), doc='Type of genomic file')
    file_format = db.Column(db.Text(), doc='Size of file in bytes')
    is_harmonized = db.Column(db.Boolean(), doc='Whether or not the file'
                              ' is harmonized')
    reference_genome = db.Column(db.Text(), doc='Original reference genome of'
                                 ' the unharmonized genomic files')
    controlled_access = db.Column(db.Boolean(), doc='Whether or not the file'
                                  'is controlled access')
    latest_did = db.Column(UUID(), nullable=False)
    sequencing_experiment_id = db.Column(KfId(),
                                         db.ForeignKey(
                                         'sequencing_experiment.kf_id'),
                                         nullable=False)
    biospecimen_id = db.Column(KfId(), db.ForeignKey('biospecimen.kf_id'),
                               nullable=False)

    # Fields used by indexd, but not tracked in the database
    file_name = ''
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

    return indexd.new(target)


@event.listens_for(GenomicFile, 'before_update')
def update_indexd(mapper, connection, target):
    """
    Updates a document in indexd
    """
    return indexd.update(target)


@event.listens_for(GenomicFile, 'before_delete')
def delete_indexd(mapper, connection, target):
    """
    Deletes a document in indexd
    """
    # Get the current revision if not already loaded
    if target.rev is None:
        target.merge_indexd()

    indexd.delete(target)
