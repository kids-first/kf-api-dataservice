from itertools import chain

from sqlalchemy import and_, event

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype


class AliasGroup(db.Model, Base):
    """
    Alias group.

    Each record in this table represents a group of particpants who are
    aliased to each other (they are all the same person, but have distinct
    entries in the participant table). Participants with the same
    alias_group_id are all aliases of each other.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = "alias_group"
    __prefix__ = 'AG'

    participants = db.relationship('Participant',
                                   backref='alias_group')


class Participant(db.Model, Base):
    """
    Participant entity.

    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to participant by contributor
    :param family_id: Id for the participants grouped by family
    :param is_proband: Denotes whether participant is proband of study
    :param consent_type: Type of the consent participant belongs to
    :param race: Race of participant
    :param ethnicity: Ethnicity of participant
    :param gender: Self reported gender of participant
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = 'participant'
    __prefix__ = 'PT'

    external_id = db.Column(db.Text(), doc='ID used by external study')
    family_id = db.Column(KfId(),
                          db.ForeignKey('family.kf_id'),
                          nullable=True,
                          doc='Id for the participants grouped by family')
    is_proband = db.Column(
        db.Boolean(),
        nullable=False,
        doc='Denotes whether participant is proband of study')
    consent_type = db.Column(db.Text(),
                             doc='Type of the consent participant belongs to')
    race = db.Column(db.Text(),
                     doc='The race of the participant')
    ethnicity = db.Column(db.Text(),
                          doc='The ethnicity of the participant')
    gender = db.Column(db.Text(),
                       doc='The gender of the participant')
    diagnoses = db.relationship(Diagnosis,
                                cascade='all, delete-orphan',
                                backref=db.backref('participant',
                                                   lazy=True))
    biospecimens = db.relationship(Biospecimen, backref='participant',
                                   cascade='all, delete-orphan')
    outcomes = db.relationship(Outcome,
                               cascade='all, delete-orphan',
                               backref=db.backref('participant',
                                                  lazy=True))
    phenotypes = db.relationship(Phenotype,
                                 cascade='all, delete-orphan',
                                 backref=db.backref('participant',
                                                    lazy=True))

    study_id = db.Column(KfId(),
                         db.ForeignKey('study.kf_id'),
                         nullable=False)

    alias_group_id = db.Column(KfId(), db.ForeignKey('alias_group.kf_id'))

    def add_alias(self, pt):
        """
        A convenience method to make participant 'pt'
        an alias of participant 'self'.

        There are 4 cases to consider:

        1) Participant pt and self have not been assigned an alias
        group. Create a new alias group and add both particpants to it.

        2) Participant pt does not have an alias group, but participant self
        does. Add pt to self's alias group.

        3) Participant self does not have an alias group but particpant pt
        does. Add self to pt's alias group

        4) Both participants already have an alias group. Find which particpant
        has the smaller alias group and merge all particpants in the
        smaller group into the larger group

        ** NOTE ** A particpant's aliases can also be created manually by
        direct manipulation of the particpants in an AliasGroup or
        the particpant's alias_group_id. However, then it is completely up to
        the user to ensure all aliases are in the right group and there aren't
        redundant groups that exist.
        """
        # Neither particpant has an alias group yet
        if (not pt.alias_group) and (not self.alias_group):
            g = AliasGroup()
            g.participants.extend([self, pt])

        # Self belongs to alias group, pt does not
        elif (not pt.alias_group) and (self.alias_group):
            self.alias_group.particpants.append(pt)

        # pt belongs to an alias group, self does not
        elif pt.alias_group and (not self.alias_group):
            pt.alias_group.particpants.append(self)

        # Both particpants belong to two different alias groups
        elif pt.alias_group and self.alias_group:
            # Find smaller alias group first
            c1 = (Participant.query.
                  filter_by(alias_group_id=self.alias_group_id).count())
            c2 = (Participant.query.
                  filter_by(alias_group_id=pt.alias_group_id).count())

            smaller_alias_group = self.alias_group
            larger_alias_group = pt.alias_group
            if c2 <= c1:
                larger_alias_group = self.alias_group
                smaller_alias_group = pt.alias_group

            # Merge smaller alias group with larger alias group
            # aka, change all participants' alias_group_id in the smaller group
            # to be the alias_group_id of the larger group
            for p in (db.session.query(Participant).
                      filter(Participant.alias_group_id ==
                             smaller_alias_group.kf_id)):
                p.alias_group = larger_alias_group

            # Delete old alias group
            db.session.delete(smaller_alias_group)

    @property
    def aliases(self):
        """
        Retrieve aliases of participant

        Return all participants with same alias group id
        """
        if self.alias_group:
            return [pt for pt in Participant.query.filter(
                and_(Participant.alias_group_id == self.alias_group_id),
                Participant.kf_id != self.kf_id)
            ]
        else:
            return []

    def __repr__(self):
        return '<Participant {}>'.format(self.kf_id)


@event.listens_for(Participant, 'after_delete')
def delete_orphans(mapper, connection, state):
    q = (db.session.query(AliasGroup)
         .filter(~AliasGroup.participants.any()))
    q.delete(synchronize_session='fetch')
