from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.aliquot.models import Aliquot


class Sample(db.Model, Base):
    """
    Sample entity.
    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sample by contributor
    :param composition : The cellular composition of the sample.
    :param tissue_type: description of the kind of tissue collected
           with respect to disease status or proximity to tumor tissue
    :param anatomical_site : The name of the primary disease site of the
           submitted tumor sample
    :param age_at_event_days: Age at the time sample was
            acquired, expressed in number of days since birth
    :param tumor_descriptor: The kind of disease present in the tumor
           specimen as related to a specific timepoint
    :param uberon: Uber-anatomy ontology for anatomical_site
    """
    __tablename__ = 'sample'
    __prefix__ = 'SA'

<<<<<<< HEAD
    external_id = db.Column(db.Text(),
                            doc='Identifier used by external systems')
    tissue_type = db.Column(db.Text(),
                            doc='Description of the kind of sample collected')
    composition = db.Column(db.Text(),
                            doc='The cellular composition of the sample')
    anatomical_site = db.Column(db.Text(),
                                doc='The anatomical location of collection')
    age_at_event_days = db.Column(db.Integer(),
                                  doc='Age at the time of event occurred in '
                                      'number of days since birth.')
    tumor_descriptor = db.Column(db.Text(),
                                 doc='Disease present in the sample')
    uberon = db.Column(db.Text())
    aliquots = db.relationship(Aliquot, backref='samples',
                               cascade="all, delete-orphan",
                               doc='kf_id of aliquots derived from the sample')
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False,
                               doc='The kf_id of the sample\'s donor')
