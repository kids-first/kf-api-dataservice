from itertools import chain

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
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
    :param family_id: Id for the participants grouped by family
    :param is_proband: Denotes whether participant is proband of study
    :param consent_type: Type of the consent participant belongs to
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = "participant"
    __prefix__ = 'PT'

    external_id = db.Column(db.Text(), doc='ID used by external study')
    family_id = db.Column(db.Text(),
                          doc='Id for the participants grouped by family')
    is_proband = db.Column(
        db.Boolean(),
        nullable=False,
        doc='Denotes whether participant is proband of study')
    consent_type = db.Column(db.Text(),
                             doc='Type of the consent participant belongs to')
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
    study_id = db.Column(KfId(),
                         db.ForeignKey('study.kf_id'),
                         nullable=False)

    def upstream_immediate_relatives(self):
        """
        Convenience method to get immediate related participants upstream of
        self.

        An upstream relative is the participant pointing to self in the family
        relationship.
        For example for the family relationship: P1 --> P2 (where P2 is self),
        P1 is the upstream relative of P2.
        """
        for r in self.incoming_family_relationships:
            yield r.participant

    def downstream_immediate_relatives(self):
        """
        Convenience method to get related immediate relatives downstream from
        self.

        A downstream relative is the participant that self points to in the
        family relationship.
        For example for the family relationship: P1 --> P2 (where P1 is self),
        P2 is the downstream relative of P1.
        """
        for r in self.outgoing_family_relationships:
            yield r.relative

    def immediate_relatives(self):
        """
        Convenience method to get all immediate relatives of this participant
        """
        return chain(self.upstream_immediate_relatives(),
                     self.downstream_immediate_relatives())

    def __repr__(self):
        return '<Participant {}>'.format(self.kf_id)
