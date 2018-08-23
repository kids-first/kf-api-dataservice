from sqlalchemy import event

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.genomic_file.models import GenomicFile


class ReadGroup(db.Model, Base):
    """
    ReadGroup entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sequencing experiment by contributor
    :param paired_end: The direction of the read
    :param flow_cell: The identifier for the group's flow cell
    :param lane_number: The group's lane
    :param quality_scale: The quality score encoding of the fastq file
    """
    __tablename__ = 'read_group'
    __prefix__ = 'RG'

    external_id = db.Column(db.Text(), nullable=True,
                            doc='Name given to read group by the contributor')
    flow_cell = db.Column(db.Text(),
                          doc='The identifier of the group\'s flow cell')
    lane_number = db.Column(db.Float(),
                            doc='The group\'s lane')
    quality_scale = db.Column(db.Text(),
                              doc='The scale used to encode quality scores')

    genomic_files = db.relationship('GenomicFile',
                                    secondary='read_group_genomic_file',
                                    backref=db.backref('read_groups'))


class ReadGroupGenomicFile(db.Model, Base):
    """
    Represents association table between read_group table and
    genomic_file table. Contains all read_group, genomic_file combiniations.
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = 'read_group_genomic_file'
    __prefix__ = 'RF'
    __table_args__ = (db.UniqueConstraint('read_group_id',
                                          'genomic_file_id'),)
    read_group_id = db.Column(KfId(),
                              db.ForeignKey('read_group.kf_id'),
                              nullable=False)

    genomic_file_id = db.Column(KfId(),
                                db.ForeignKey('genomic_file.kf_id'),
                                nullable=False)
    read_group = db.relationship('ReadGroup')
    genomic_file = db.relationship('GenomicFile')

    def __repr__(self):
        return "{}-{}".format(self.read_group.external_id,
                              self.genomic_file.external_id)


@event.listens_for(GenomicFile, 'after_delete')
def delete_orphans(mapper, connection, state):
    q = (db.session.query(ReadGroup)
         .filter(~ReadGroup.genomic_files.any()))
    q.delete(synchronize_session='fetch')
