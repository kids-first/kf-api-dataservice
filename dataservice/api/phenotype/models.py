from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class Phenotype(db.Model, Base):
    """
    Phenotype entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param phenotype: Name given to Phenotype by contributor
    :param hpo_id: The ID of the term from the Human Phenotype Ontology
     which represents a harmonized phenotype
    :param snomed_id: The ID of the term from Systematized Nomenclature of
     Medicine -- Clinical Terms which encodes clinical terminology
    :param observed: whether phenotype is negative or positive
    :param age_at_event_days: Age at the time phenotype was
            observed, expressed in number of days since birth
    """
    __tablename__ = 'phenotype'
    __prefix__ = 'PH'

    phenotype = db.Column(db.Text(),
                          doc='Name given to Phenotype by contributor')
    hpo_id = db.Column(db.Text(),
                       doc='The ID of the term from Human Phenotype Ontology '
                       'which represents a harmonized phenotype')
    snomed_id = db.Column(db.Text(),
                          doc='The ID of the term from Systematized '
                          'Nomenclature of Medicine -- Clinical Terms which '
                          'encodes clinical terminology')
    observed = db.Column(db.Text(),
                         doc='whether phenotype is negative or positive')
    age_at_event_days = db.Column(db.Integer(),
                                  doc='Age at the time of event occurred in '
                                      'number of days since birth')
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False)
