from sqlalchemy import event

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.participant.models import Participant

REVERSE_RELS = {
    'mother': 'child',
    'father': 'child',
    'sister': 'sister',
    'brother': 'brother'
}


class FamilyRelationship(db.Model, Base):
    """
    Represents a relationship between two family members.

    The relationship table represents a directed graph. One or more
    relationships may exist between any two participants.
    (P1 -> P2 is different than P2 -> P1)

    :param kf_id: Primary key given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param participant_id: Kids first id of the first Participant in the
    relationship
    :param relative_id: Kids first id of the second Participant (or relative)
    in the relationship
    :param relationship_type: Text describing the nature of the
    relationship (i.e. father, mother, sister, brother)
    :param _rel_name: an autogenerated parameter used to ensure that the
    relationships are not duplicated and the graph is undirected
    """
    __tablename__ = 'family_relationship'
    __prefix__ = 'FR'
    __table_args__ = (db.UniqueConstraint('participant_id', 'relative_id',
                                          'participant_to_relative_relation',
                                          'relative_to_participant_relation'),)

    participant_id = db.Column(
        KfId(),
        db.ForeignKey('participant.kf_id'), nullable=False)

    relative_id = db.Column(
        KfId(),
        db.ForeignKey('participant.kf_id'), nullable=False)

    participant_to_relative_relation = db.Column(db.Text(), nullable=False)

    relative_to_participant_relation = db.Column(db.Text())

    participant = db.relationship(
        Participant,
        primaryjoin=participant_id == Participant.kf_id,
        backref=db.backref('outgoing_family_relationships',
                           cascade='all, delete-orphan'))

    relative = db.relationship(
        Participant,
        primaryjoin=relative_id == Participant.kf_id,
        backref=db.backref('incoming_family_relationships',
                           cascade='all, delete-orphan'))

    def __repr__(self):
        return '<{} is {} of {}>'.format(self.participant,
                                         self.participant_to_relative_relation,
                                         self.relative)


@event.listens_for(FamilyRelationship.participant_to_relative_relation, 'set')
def set_reverse_relation(target, value, oldvalue, initiator):
    """
    Listen for set 'participant_to_relative_relation' events and
    set the reverse relationship, 'relative_to_participant_relation' attribute
    """
    target.relative_to_participant_relation = REVERSE_RELS.get(value, None)
