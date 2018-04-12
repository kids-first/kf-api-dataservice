import random

from sqlalchemy.exc import IntegrityError

from dataservice.extensions import db
from dataservice.api.participant.models import Participant, AliasGroup
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def _create_save_participants(self, n=5):
        """
        Create participants
        """
        s = Study(external_id='phs001')

        particpant_data = {}
        for i in range(n):
            k = 'p{}'.format(i)
            particpant_data[k] = {
                'external_id': k,
                'is_proband': random.choice([True, False])
            }
            pt = Participant(**particpant_data[k])
            particpant_data[k]['obj'] = pt
            s.participants.append(pt)

        db.session.add(s)
        db.session.commit()

        return particpant_data

    def _create_save_to_db(self, n=5):
        """
        Create participants and aliases
        """
        data = self._create_save_participants()
        # Add p1 as alias of p0
        p0 = data['p0']['obj']
        p1 = data['p1']['obj']
        p0.add_alias(p1)

        # Add p3 as alias of p2
        p2 = data['p2']['obj']
        p3 = data['p3']['obj']
        p2.add_alias(p3)

        # Add p2 as an alias of p0
        p0.add_alias(p2)

        db.session.commit()

        return data

    def test_create_and_get(self):
        """
        Test create participant alias
        """
        data = self._create_save_participants()
        alias_data = {
            'g1': ['p0', 'p1'],
            'g2': ['p2', 'p3']
        }

        # Add p1 as alias of p0
        p0 = data['p0']['obj']
        p1 = data['p1']['obj']
        p0.add_alias(p1)

        # Add p3 as alias of p2
        p2 = data['p2']['obj']
        p3 = data['p3']['obj']
        p2.add_alias(p3)

        db.session.commit()

        # Check that 2 alias groups exist
        self.assertEqual(2, AliasGroup.query.count())
        # Check that 2 participants are in each alias group
        for g in AliasGroup.query.all():
            self.assertEqual(2, len(g.participants))
        # Check that the right participants are in each alias group
        # and have correct aliases
        for group, pt_ids in alias_data.items():
            pts = Participant.query.filter(Participant.external_id.in_(pt_ids))
            for pt in pts:
                alias_ids = [a.external_id for a in pt.aliases]
                self.assertEqual(set(alias_ids), set(pt_ids) - {pt.external_id})

        # Add p2 as an alias of p0 - tests merging two different alias groups
        p0 = Participant.query.get(data['p0']['obj'].kf_id)
        p2 = Participant.query.get(data['p2']['obj'].kf_id)
        p0.add_alias(p2)
        db.session.commit()

        # Check that 1 alias groups exists
        self.assertEqual(1, AliasGroup.query.count())
        # Check that 4 participants are in the alias group
        g = AliasGroup.query.first()
        self.assertEqual(4, len(g.participants))
        pt_ids = set(data.keys())
        pt_ids.remove('p4')
        # Check that the right participants are in each alias group
        # and have correct aliases
        pts = Participant.query.filter(Participant.external_id.in_(pt_ids))
        for pt in pts:
            alias_ids = [a.external_id for a in pt.aliases]
            self.assertEqual(set(alias_ids), pt_ids - {pt.external_id})

    def test_update(self):
        """
        Test update particpant alias
        """
        data = self._create_save_to_db()

        # Remove p0 from alias group
        g = AliasGroup.query.first()
        p0 = Participant.query.get(data['p0']['obj'].kf_id)
        g.participants.remove(p0)
        db.session.commit()

        # p0 should have no alias group, alias group should not have p0
        self.assertIs(p0.alias_group_id, None)
        self.assertIs(p0.alias_group, None)
        g = AliasGroup.query.first()
        self.assertNotIn(p0, g.participants)

        # Check aliases of other particpants in group
        for p in g.participants:
            self.assertEqual(2, len(p.aliases))

    def test_invalid_alias(self):
        """
        Test updating participant alias group to invalid values
        1) add to non existent alias group
        """
        data = self._create_save_to_db()

        # Non-existent alias group
        p0 = Participant.query.get(data['p0']['obj'].kf_id)
        p0.alias_group_id = '00000000000'
        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()
        self.assertEqual(3, len(p0.aliases))

    def test_add_multiple(self):
        """
        Test adding particpant to more than one alias group
        """
        data = self._create_save_to_db()
        g_kf_id = AliasGroup.query.first().kf_id

        # Try to add to than one alias group
        p0 = Participant.query.get(data['p0']['obj'].kf_id)
        g = AliasGroup()
        g.participants.append(p0)
        db.session.add(g)
        db.session.commit()

        # p0 should be in new alias group, but have no aliases
        # (since a participant cannot be an alias of itself)
        self.assertEqual(0, len(p0.aliases))

        # Add p1 as an alias of p0
        p1 = Participant.query.get(data['p1']['obj'].kf_id)
        p0.add_alias(p1)
        db.session.commit()

        # Now there should only be 1 alias group again since the 2 groups merged
        self.assertEqual(1, AliasGroup.query.count())
        self.assertEqual(4, len(AliasGroup.query.first().participants))

        # Smaller group should not exist, since it should be merged into larger
        self.assertEqual(g_kf_id, AliasGroup.query.first().kf_id)

    def test_delete(self):
        """
        Test remove participant alias
        """
        data = self._create_save_to_db()

        # Remove particpant's alias group
        p0 = Participant.query.get(data['p0']['obj'].kf_id)
        g = AliasGroup.query.first()
        g.participants.remove(p0)
        db.session.commit()

        # p0 should have no assigned alias group
        self.assertIs(None, p0.alias_group)

        # Other particpants in alias group should have 1 less alias
        p1 = Participant.query.get(data['p1']['obj'].kf_id)
        self.assertEqual(2, len(p1.aliases))

        # Delete particpant
        db.session.delete(p1)
        db.session.commit()

        # Other particpants in alias group should have 1 less alias
        p2 = Participant.query.get(data['p2']['obj'].kf_id)
        self.assertEqual(1, len(p2.aliases))

        # Delete an alias group
        db.session.delete(g)
        db.session.commit()

        # All remaining particpants should exist and have no aliases
        self.assertEqual(4, Participant.query.count())
        for p in Participant.query.all():
            self.assertEqual(0, len(p.aliases))
