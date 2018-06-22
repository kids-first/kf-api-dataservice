from sqlalchemy.exc import IntegrityError

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.family.models import Family
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
                self.assertIn(p3, self._all_participants(p))
            if p.external_id == 'Pebbles':
                for participant2 in [p1, p2, p4, p5]:
                    self.assertIn(participant2, self._all_participants(p))
            if p.external_id == 'Dino':
                self.assertIn(p3, self._all_participants(p))
            if p.external_id == 'Bart':
                self.assertIn(p3, self._all_participants(p))
        for r in FamilyRelationship.query.all():
            self.assertEqual(r.participant2_to_participant1_relation,
                             REVERSE_RELS.get(
                                 r.participant1_to_participant2_relation))

    def test_directed_graph_and_multiple_edges(self):
        """
        Test that multiple relationships can exist between a
        pair of participants, including reverse relationships
        """
        # Create relationships
        self._create_relationships()
        r = FamilyRelationship.query.first()
        rev_rel_str = 'reversed {}'.format(
            r.participant1_to_participant2_relation)

        reverse_r = FamilyRelationship(
            participant1=r.participant2,
            participant2=r.participant1,
            participant1_to_participant2_relation=rev_rel_str)

        new_r = FamilyRelationship(
            participant1_id=r.participant1_id,
            participant2_id=r.participant2_id,
            participant1_to_participant2_relation='weirdness')

        db.session.add(reverse_r)
        db.session.add(new_r)
        db.session.commit()

        self.assertEqual(
            FamilyRelationship.query.filter_by(
                participant1_to_participant2_relation=rev_rel_str).first(),
            reverse_r)
        self.assertEqual(
            FamilyRelationship.query.filter_by(
                participant1_to_participant2_relation='weirdness').first(),
            new_r)

    def test_find(self):
        """
        Test find relationship
        """
        self._create_relationships()

        # Find relationship starting at Fred
        p = Participant.query.filter_by(external_id='Fred').one()
        rel = FamilyRelationship.query.filter_by(participant1=p).one()
        self.assertEqual('Fred', rel.participant1.external_id)

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
        rel = FamilyRelationship.query.filter_by(participant1=p).one()

        # Update Fred's relationship
        rel.participant2 = susy
        rel.participant1_to_participant2_relation = 'daughter'
        db.session.commit()

        # Check database
        rel = FamilyRelationship.query.filter_by(participant1=p).one()
        pebbles = Participant.query.filter_by(external_id='Pebbles').one()
        self.assertNotIn(pebbles, self._all_participants(p))
        self.assertIn(susy, self._all_participants(p))
        self.assertEqual('daughter', rel.participant1_to_participant2_relation)

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
        participant1_id = rel.participant1.kf_id
        participant2_id = rel.participant2.kf_id

        # Save to database
        db.session.delete(rel)
        db.session.commit()

        # Check database
        rel = FamilyRelationship.query.get(rel_kf_id)
        # Rel deleted
        self.assertEqual(rel, None)
        # Participants still exist
        self.assertEqual(participant1_id,
                         Participant.query.get(participant1_id).kf_id)
        self.assertEqual(participant2_id,
                         Participant.query.get(participant2_id).kf_id)

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
            'participant1_to_participant2_relation': 'father',
            'participant1_id': 'FR_00000000',
            'participant2_id': 'FR_00000001'
        }
        r = FamilyRelationship(**data)

        # Add to db
        db.session.add(r)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_case_sensitivity(self):
        """
        Test that relationships are created w proper label regardless of case
        """
        study = Study(external_id='study')
        p1 = Participant(external_id='P0', is_proband=False)
        p2 = Participant(external_id='P1',  is_proband=False)
        study.participants.extend([p1, p2])

        # Create relationships
        r = FamilyRelationship(participant1=p1, participant2=p2,
                               participant1_to_participant2_relation='Father')
        count = FamilyRelationship.query.count()
        db.session.add(study)
        db.session.add(r)
        db.session.commit()

        kf_id = r.kf_id
        assert count + 1 == FamilyRelationship.query.count()
        # Original value goes in as is
        assert 'Father' == r.participant1_to_participant2_relation
        # Correct reverse relation selected
        assert 'Child' == r.participant2_to_participant1_relation

        r.participant1_to_participant2_relation = 'mother'
        db.session.commit()

        # Original value as is, proper reverse relation selected
        r = FamilyRelationship.query.get(kf_id)
        assert 'mother' == r.participant1_to_participant2_relation
        assert 'Child' == r.participant2_to_participant1_relation

        r.participant1_to_participant2_relation = 'Sibling'
        db.session.commit()

        # Original value as is, proper reverse relation selected
        r = FamilyRelationship.query.get(kf_id)
        assert 'Sibling' == r.participant1_to_participant2_relation
        assert 'Sibling' == r.participant2_to_participant1_relation

    def test_not_null_constraint(self):
        """
        Test that a family relationship cannot be created without required
        parameters such as participant2, participant2_id,
        participant1_to_participant2_relation
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
        db.session.add(r)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Missing 1 required param
        data = {
            'participant1_id': p1.kf_id
        }
        r = FamilyRelationship(**data)
        # Check database
        db.session.add(r)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Missing 2 required param
        data = {
            'participant1_id': p1.kf_id,
            'participant2_id': p2.kf_id
        }
        r = FamilyRelationship(**data)
        # Check database
        db.session.add(r)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_query_all_relationships(self):
        """
        Test the class method query_all_relationships on FamilyRelationship

        Given a participant's kf_id, this method should return all of the
        biological family relationships of that participant and relationships
        of the family members.

        If the participant does not have a family defined, then
        query_all_relationships will return all of the immediate/direct family
        relationships of the participant.
        """
        p1, p2, p3, p4, p5, study = self._create_relationships()

        # Add 2nd first gen child to family
        p6 = Participant(external_id='Bloo', is_proband=True,
                         study_id=study.kf_id)
        r5 = FamilyRelationship(participant1=p1, participant2=p6,
                                participant1_to_participant2_relation='father')
        r6 = FamilyRelationship(participant1=p2, participant2=p6,
                                participant1_to_participant2_relation='mother')
        db.session.add_all([r5, r6])
        db.session.commit()

        # Case 1 - Participant does not have a family defined
        kf_id = p3.kf_id
        q = FamilyRelationship.query_all_relationships(kf_id)
        # Only immediate family relationships of p3 are returned
        self.assertEqual(4, q.count())
        pts = self._immediate_relationship_counts(q.all())
        self.assertEqual(4, pts.get(kf_id))

        # Case 2 - Participant has a family defined
        f1 = Family(external_id='f1')
        for p in Participant.query.all():
            p.family = f1
        db.session.commit()
        q = FamilyRelationship.query_all_relationships(kf_id)
        # All family relationships in p3's family are returned
        self.assertEqual(6, q.count())
        pts = self._immediate_relationship_counts(q.all())
        # p3 has same # of direct/immediate relationships as before
        self.assertEqual(4, pts.get(kf_id))

        # Get all
        q = FamilyRelationship.query_all_relationships()
        self.assertEqual(6, q.count())

        # Non existent participant
        q = FamilyRelationship.query_all_relationships('PT_00001111')
        self.assertEqual(0, q.count())

        # Family but no family relationships defined
        FamilyRelationship.query.delete()
        db.session.commit()
        q = FamilyRelationship.query_all_relationships(None)
        self.assertEqual(0, q.count())

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
        r1 = FamilyRelationship(participant1=p1, participant2=p3,
                                participant1_to_participant2_relation='father')
        r2 = FamilyRelationship(participant1=p2, participant2=p3,
                                participant1_to_participant2_relation='mother')
        r3 = FamilyRelationship(participant1=p3, participant2=p4,
                                participant1_to_participant2_relation='father')

        r4 = FamilyRelationship(participant1=p3, participant2=p5,
                                participant1_to_participant2_relation='cousin')

        db.session.add_all([r1, r2, r3, r4])
        db.session.commit()

        return p1, p2, p3, p4, p5, study

    def _all_participants(self, p):
        """
        Get all family relationships of a participant and return
        all of participants in those relationships
        """
        relationships = FamilyRelationship.query_all_relationships(
            p.kf_id).all()
        participants = []
        for rel in relationships:
            participants.extend([rel.participant1, rel.participant2])

        return participants

    def _immediate_relationship_counts(self, relationships):
        """
        Count # of relationships a participant appears in
        Store in dict of key=participant to value=count
        """
        def update_counts(kf_id, pts):
            if kf_id not in pts:
                pts[kf_id] = 1
            else:
                pts[kf_id] += 1
            return pts

        pts = {}
        for rel in relationships:
            pts = update_counts(rel.participant1.kf_id, pts)
            pts = update_counts(rel.participant2.kf_id, pts)

        return pts
