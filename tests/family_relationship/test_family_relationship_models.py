from sqlalchemy.exc import IntegrityError

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.family_relationship.models import (
    FamilyRelationship,
    REVERSE_RELS
)
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test FamilyRelationship database model
    """

    def test_create(self):
        """
        Test create family relationships
        """
        # Create relationships
        p1, p2, p3, p4, p5, study = self._create_relationships()

        # Check database
        for p in Participant.query.all():
            if p.external_id == 'Fred' or p.external_id == 'Wilma':
                self.assertIn(p3, self._all_relatives(p))
            if p.external_id == 'Pebbles':
                for relative in [p1, p2, p4, p5]:
                    self.assertIn(relative, self._all_relatives(p))
            if p.external_id == 'Dino':
                self.assertIn(p3, self._all_relatives(p))
            if p.external_id == 'Bart':
                self.assertIn(p3, self._all_relatives(p))
        for r in FamilyRelationship.query.all():
            self.assertEqual(r.relative_to_participant_relation,
                             REVERSE_RELS.get(
                                 r.participant_to_relative_relation))

    def test_directed_graph_and_multiple_edges(self):
        """
        Test that multiple relationships can exist between a
        pair of participants, including reverse relationships
        """
        # Create relationships
        self._create_relationships()
        r = FamilyRelationship.query.first()
        rev_rel_str = 'reversed {}'.format(r.participant_to_relative_relation)

        reverse_r = FamilyRelationship(
            participant=r.relative,
            relative=r.participant,
            participant_to_relative_relation=rev_rel_str)

        new_r = FamilyRelationship(
            participant_id=r.participant_id,
            relative_id=r.relative_id,
            participant_to_relative_relation='weirdness')

        db.session.add(reverse_r)
        db.session.add(new_r)
        db.session.commit()

        self.assertEqual(
            FamilyRelationship.query.filter_by(
                participant_to_relative_relation=rev_rel_str).first(),
            reverse_r)
        self.assertEqual(
            FamilyRelationship.query.filter_by(
                participant_to_relative_relation='weirdness').first(),
            new_r)

    def test_find(self):
        """
        Test find relationship
        """
        self._create_relationships()

        # Find relationship starting at Fred
        p = Participant.query.filter_by(external_id='Fred').one()
        rel = FamilyRelationship.query.filter_by(participant=p).one()
        self.assertEqual('Fred', rel.participant.external_id)

    def test_update(self):
        """
        Test update relationship
        """
        p1, p2, p3, p4, p5, study = self._create_relationships()

        # Create new participant
        susy = Participant(external_id='Susy', is_proband=True,
                           study_id=study.kf_id)
        db.session.add(susy)
        db.session.commit()

        # Find relationship starting at Fred
        p = Participant.query.filter_by(external_id='Fred').one()
        rel = FamilyRelationship.query.filter_by(participant=p).one()

        # Update Fred's relationship
        rel.relative = susy
        rel.participant_to_relative_relation = 'daughter'
        db.session.commit()

        # Check database
        rel = FamilyRelationship.query.filter_by(participant=p).one()
        pebbles = Participant.query.filter_by(external_id='Pebbles').one()
        self.assertNotIn(pebbles, self._all_relatives(p))
        self.assertIn(susy, self._all_relatives(p))
        self.assertEqual('daughter', rel.participant_to_relative_relation)

    def test_delete(self):
        """
        Test deleting a family relationship
        """
        # Create relationships
        self._create_relationships()

        # Get a relationsihp
        rel = FamilyRelationship.query.first()

        # Save ids
        rel_kf_id = rel.kf_id
        participant_id = rel.participant.kf_id
        relative_id = rel.relative.kf_id

        # Save to database
        db.session.delete(rel)
        db.session.commit()

        # Check database
        rel = FamilyRelationship.query.get(rel_kf_id)
        # Rel deleted
        self.assertEqual(rel, None)
        # Participants still exist
        self.assertEqual(participant_id,
                         Participant.query.get(participant_id).kf_id)
        self.assertEqual(relative_id,
                         Participant.query.get(relative_id).kf_id)

    def test_delete_via_particpant(self):
        """
        Test delete family relationships via deletion of participant
        """
        # Create relationships
        self._create_relationships()

        # Get participant to delete
        p = Participant.query.filter_by(external_id='Pebbles').one()

        # Delete participant
        db.session.delete(p)
        db.session.commit()

        # Check database
        # No fam rels should exist, Pebbles was in every relationship
        self.assertEqual(0, FamilyRelationship.query.count())

        # Rest of participants still exist
        self.assertEqual(4, Participant.query.count())

    def test_foreign_key_constraint(self):
        """
        Test that a relationship cannot be created without existing
        reference Participants. This checks foreign key constraint
        """
        # Create family relationship
        data = {
            'participant_to_relative_relation': 'father',
            'participant_id': 'non existent',
            'relative_id': 'non existent'
        }
        r = FamilyRelationship(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(r))

    def test_not_null_constraint(self):
        """
        Test that a family relationship cannot be created without required
        parameters such as participant_id, relative_id,
        participant_to_relative_relation
        """
        # Create study
        study = Study(external_id='phs001')

        # Create participants
        p1 = Participant(external_id='BobbyBooBoo', is_proband=False)
        p2 = Participant(external_id='SallyMally', is_proband=False)
        study.participants.extend([p1, p2])
        db.session.add(study)
        db.session.commit()

        # Missing all required parameters
        data = {}
        r = FamilyRelationship(**data)
        # Check database
        self.assertRaises(IntegrityError, db.session.add(r))
        db.session.rollback()

        # Missing 1 required param
        data = {
            'participant_id': p1.kf_id
        }
        r = FamilyRelationship(**data)
        # Check database
        self.assertRaises(IntegrityError, db.session.add(r))
        db.session.rollback()

        # Missing 2 required param
        data = {
            'participant_id': p1.kf_id,
            'relative_id': p2.kf_id
        }
        r = FamilyRelationship(**data)
        # Check database
        self.assertRaises(IntegrityError, db.session.add(r))

    def _create_relationships(self):
        """
        Create family relationships and required entities
        """
        # Create study
        study = Study(external_id='phs001')

        # Create participants
        # Father of p3
        p1 = Participant(external_id='Fred', is_proband=False)
        # Mother of p3, p5
        p2 = Participant(external_id='Wilma',  is_proband=False)
        # Son of p1
        p3 = Participant(external_id='Pebbles', is_proband=True)
        # Son of p3
        p4 = Participant(external_id='Dino', is_proband=True)
        # Cousin of p3
        p5 = Participant(external_id='Bart', is_proband=True)
        study.participants.extend([p1, p2, p3, p4, p5])
        db.session.add(study)
        db.session.commit()

        # Create relationships
        r1 = FamilyRelationship(participant=p1, relative=p3,
                                participant_to_relative_relation='father')
        r2 = FamilyRelationship(participant=p2, relative=p3,
                                participant_to_relative_relation='mother')
        r3 = FamilyRelationship(participant=p3, relative=p4,
                                participant_to_relative_relation='father')

        r4 = FamilyRelationship(participant=p3, relative=p5,
                                participant_to_relative_relation='cousin')

        db.session.add_all([r1, r2, r3, r4])
        db.session.commit()

        return p1, p2, p3, p4, p5, study

    def _all_relatives(self, p):
        relationships = FamilyRelationship.query_all_relationships(
            p.kf_id).all()
        relatives = []
        for rel in relationships:
            relatives.extend([rel.participant, rel.relative])

        return relatives
