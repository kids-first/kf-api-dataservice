from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.sample.models import Sample
from dataservice.api.demographic.models import Demographic
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype


class Participant(db.Model, Base):
    """
    Participant entity.

    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to participant by contributor
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = "participant"

    external_id = db.Column(db.Text())
    diagnoses = db.relationship(Diagnosis,
                                cascade="all, delete-orphan",
                                backref=db.backref('participants',
                                                   lazy=True))
    samples = db.relationship(Sample, backref='participant',
                              cascade="all, delete-orphan")
    demographic = db.relationship(Demographic, backref='participant',
                                  uselist=False, cascade="all, delete-orphan",
                                  lazy=True)
    outcomes = db.relationship(Outcome,
                               cascade="all, delete-orphan",
                               backref=db.backref('participants',
                                                  lazy=True))
    phenotypes = db.relationship(Phenotype,
                                 cascade="all, delete-orphan",
                                 backref=db.backref('participants',
                                                    lazy=True))
