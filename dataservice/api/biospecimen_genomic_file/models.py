from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class BiospecimenGenomicFile(db.Model, Base):
    """
    Represents association table between biospecimen table and
    genomic_file table. Contains all biospecimen, genomic_file combiniations.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """

    __tablename__ = 'biospecimen_genomic_file'
    __prefix__ = 'BG'
    __table_args__ = (db.UniqueConstraint('genomic_file_id',
                                          'biospecimen_id'),)
    genomic_file_id = db.Column(KfId(),
                                db.ForeignKey('genomic_file.kf_id'),
                                nullable=False)

    biospecimen_id = db.Column(KfId(),
                               db.ForeignKey('biospecimen.kf_id'),
                               nullable=False)
