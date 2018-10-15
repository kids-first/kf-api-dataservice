from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


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

    genomic_files = association_proxy(
        'read_group_genomic_files',
        'genomic_file',
        creator=lambda gf: ReadGroupGenomicFile(genomic_file=gf))

    read_group_genomic_files = db.relationship('ReadGroupGenomicFile',
                                               backref='read_group',
                                               cascade='all, delete-orphan')


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
                                          'genomic_file_id',),)
    read_group_id = db.Column(KfId(),
                              db.ForeignKey('read_group.kf_id'),
                              nullable=False)

    genomic_file_id = db.Column(KfId(),
                                db.ForeignKey('genomic_file.kf_id'),
                                nullable=False)
    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')


@event.listens_for(ReadGroupGenomicFile, 'after_delete')
def delete_orphans(mapper, connection, state):
    q = (db.session.query(ReadGroup)
         .filter(~ReadGroup.read_group_genomic_files.any()))
    q.delete(synchronize_session='fetch')
