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
    paired_end = db.Column(db.Integer(),
                           doc='The direction of the read')
    flow_cell = db.Column(db.Text(),
                          doc='The identifier of the group\'s flow cell')
    lane_number = db.Column(db.Float(),
                            doc='The group\'s lane')
    quality_scale = db.Column(db.Text(),
                              doc='The scale used to encode quality scores')
    genomic_file_id = db.Column(KfId(), db.ForeignKey('genomic_file.kf_id'),
                                nullable=False)
