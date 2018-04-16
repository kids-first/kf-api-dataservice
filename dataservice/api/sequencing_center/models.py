from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.biospecimen.models import Biospecimen


class SequencingCenter(db.Model, Base):
    """
    SequencingExperiment entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param name: Name given to sequencing center by contributor
    """
    __tablename__ = 'sequencing_center'
    __prefix__ = 'SC'
    name = db.Column(db.Text(), nullable=False,
                     doc='Name given to sequencing center by contributor')
    sequencing_experiment_id = db.Column(
                                         KfId(),
                                         db.ForeignKey(
                                                       'sequencing'
                                                       '_experiment.kf_id'),
                                         nullable=False,
                                         doc='The kf_id of the sequencing'
                                         ' experiment')
    biospecimens = db.relationship(Biospecimen,
                                   cascade="all, delete-orphan",
                                   backref=db.backref(
                                        'sequencing_center',
                                        lazy=True))
