from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class Container(db.Model, Base):
    """
    Container entity

    This table is being added in order to represent the Sample, Container
    concepts and their parent child relationship without affecting the
    current Biospecimen entity

    The Container can be thought of as synonymous with Biospecimen. There
    should be a 1-to-1 relationship between Container and Biospecimen

    :param kf_id: Unique id given by the Kid's First DCC
    :param external_aliquot_id: Name given to aliquot by contributor. Will be
    populated from the related Biospecimen
    :param specimen_status: Whether the container was shipped, sequenced, etc
    """

    __tablename__ = 'container'
    __prefix__ = 'CT'

    # Enforce the 1-to-1 relationship between Biospecimen and Container
    __table_args__ = (db.UniqueConstraint('biospecimen_id', ),)

    external_aliquot_id = db.Column(
        db.Text(),
        doc='Name given to aliquot by contributor'
    )
    specimen_status = db.Column(
        db.Text(),
        doc='Whether container was shipped, sequenced, etc'
    )
    biospecimen_id = db.Column(
        KfId(),
        db.ForeignKey('biospecimen.kf_id'),
        nullable=False,
        doc='The kf_id of the container\'s specimen'
    )
    sample_id = db.Column(
        KfId(),
        db.ForeignKey('sample.kf_id'),
        nullable=False,
        doc='The kf_id of the container\'s sample'
    )
