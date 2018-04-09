from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from sqlalchemy.dialects.postgresql import UUID
from dataservice.api.sequencing_experiment.models import SequencingExperiment


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
    sequencing_experiments = db.relationship(SequencingExperiment,
                                             cascade="all, delete-orphan",
                                             backref=db.backref(
                                                                'sequencing'
                                                                '_experiments',
                                                                lazy=True),
                                             doc='kf_id of sequencing '
                                             'experiments this genomic file'
                                             ' was used in')
    biospecimen_id = db.Column(KfId(), db.ForeignKey('biospecimen.kf_id'),
                               nullable=False)
