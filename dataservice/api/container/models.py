from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class Container(db.Model, Base):
    """
    Container - a distinct portion of a Sample

    The Container can be thought of as synonymous with Biospecimen. There
    should be a 1-to-1 relationship between Container and Biospecimen

    Background:

    The current Biospecimen table does not adequately model the hierarchical
    relationship between specimen groups and specimens. The Sample and
    Container tables have been created to fill in this gap.

    A Sample is a biologically equivalent group of specimens. A Container
    represents one of the specimens in the Sample's group of specimens.

    The Sample and Container tables were created in order to minimize any
    changes to the existing Biospecimen table.

    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to aliquot by contributor
    :param specimen_status: Whether the container was shipped, sequenced, etc
    """

    __tablename__ = 'container'
    __prefix__ = 'CT'

    # Enforce the 1-to-1 relationship between Biospecimen and Container
    __table_args__ = (db.UniqueConstraint('biospecimen_id', ),)

    external_id = db.Column(
        db.Text(),
        doc='Name or ID given to biospecimen by contributor'
    )
    volume_ul = db.Column(
        db.Float(),
        doc='The volume of the aliquot container in microliters'
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
