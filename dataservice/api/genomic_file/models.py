from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from sqlalchemy.dialects.postgresql import UUID


class GenomicFile(db.Model, Base):
    """
    GenomicFile entity.

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
    :param is_harmonized: whether or not the file is harmonized
    :param original_reference_genome: original reference genome of the
     unharmonized genomic files
    """
    __tablename__ = 'genomic_file'
    __prefix__ = 'GF'

    file_name = db.Column(db.Text())
    data_type = db.Column(db.Text())
    file_format = db.Column(db.Text())
    file_size = db.Column(db.BigInteger())
    file_url = db.Column(db.Text())
    is_harmonized = db.Column(db.Boolean())
    original_reference_genome = db.Column(db.Text())
    # See link for why md5sum should use uuid type
    # https://dba.stackexchange.com/questions/115271/what-is-the-optimal-data-type-for-an-md5-field
    md5sum = db.Column(UUID(), unique=True)
    controlled_access = db.Column(db.Boolean())
    sequencing_experiment_id = db.Column(KfId(),
                                         db.ForeignKey(
                                         'sequencing_experiment.kf_id'),
                                         nullable=False)
