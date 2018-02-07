from dataservice.extensions import db
from dataservice.api.common.model import Base
from sqlalchemy.dialects.postgresql import UUID

# TODO May want to change all uuid strings postgres UUID later on


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
    :param file_url: Location of file
    :param md5sum: 128 bit md5 hash of file
    :param controlled_access: whether or not the file is controlled access
    """

    __tablename__ = 'genomic_file'
    file_name = db.Column(db.Text())
    data_type = db.Column(db.Text())
    file_format = db.Column(db.Text())
    file_url = db.Column(db.Text())
    # TODO Change to use UUID for md5sum later on
    # See link for why md5sum should use uuid type
    # https://dba.stackexchange.com/questions/115271/what-is-the-optimal-data-type-for-an-md5-field
    md5sum = db.Column(UUID(), unique=True)
    controlled_access = db.Column(db.Boolean())
    sequencing_experiment_id = db.Column(db.String(8),
                                         db.ForeignKey(
                                         'sequencing_experiment.kf_id'),
                                         nullable=False)
