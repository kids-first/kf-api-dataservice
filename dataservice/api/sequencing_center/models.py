from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_experiment.models import SequencingExperiment


class SequencingCenter(db.Model, Base):
    """
    SequencingExperiment entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sequencing center by contributor
    :param name: Name given to sequencing center by contributor
    """
    __tablename__ = 'sequencing_center'
    __prefix__ = 'SC'
    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    name = db.Column(db.Text(), nullable=False, unique=True,
                     doc='Name given to sequencing center by contributor')
    sequencing_experiments = db.relationship(SequencingExperiment,
                                             backref=db.backref(
                                               'sequencing_center',
                                               lazy=True))
    biospecimens = db.relationship(Biospecimen,
                                   backref=db.backref(
                                        'sequencing_center',
                                        lazy=True))
