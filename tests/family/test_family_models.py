from dataservice.extensions import db
from dataservice.api.family.models import Family
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase


class FamilyModelTest(FlaskTestCase):
    """
    Test family database model
    """

    def _make_family(self, external_id='FAM01'):
        """
        Make a family with two participants and a given external id
        """
        s = Study(external_id='phs001')
        p1 = Participant(external_id="CASE01",
                        is_proband=False, consent_type="GRU-IRB")
        p2 = Participant(external_id="CASE02",
                        is_proband=False, consent_type="GRU-IRB")
        s.participants.extend([p1, p2])

        f = Family(external_id=external_id)
        f.participants.extend([p1, p2])
        db.session.add(s)
        db.session.commit()
        return f

    def test_create_family(self):
        """
        Test creation of a family
        """
        f = self._make_family()

        fam = Family.query.filter_by(external_id="FAM01").one()

        self.assertEqual(len(fam.participants), 2)
        self.assertTrue(fam.participants[0].external_id.startswith('CASE0'))
        self.assertTrue(fam.participants[1].external_id.startswith('CASE0'))

        p = Participant.query.filter_by(external_id="CASE01").one()
        self.assertEqual(p.family_id, fam.kf_id)

    def test_delete_family(self):
        """
        Test that a family is remove without removing participants
        """
        f = self._make_family()

        fam = Family.query.filter_by(external_id="FAM01").one()
        db.session.delete(fam)
        db.session.commit()

        self.assertEqual(Participant.query.count(), 2)
        self.assertEqual(Family.query.count(), 0)

    def test_no_multi_family(self):
        """
        Test that participants are only registered on one family at a time
        """
        f1 = self._make_family('FAM01')
        f2 = self._make_family('FAM02')

        self.assertEqual(len(f1.participants), 2)
        self.assertEqual(len(f2.participants), 2)
        # Move participant from first family to second
        p1 = f1.participants[0]
        f2.participants.append(p1)
        db.session.commit()
        # Make sure that participant moved successfully
        self.assertEqual(len(f1.participants), 1)
        self.assertEqual(len(f2.participants), 3)
        self.assertEqual(p1.family_id, f2.kf_id)

    def test_update_family(self):
        """
        Test that family properties may be updated
        """
        f = self._make_family('FAM01')
        self.assertEqual(f.external_id, 'FAM01')
        f.external_id = 'FAMXX'
        db.session.commit()
        self.assertEqual(Family.query.get(f.kf_id).external_id, 'FAMXX')
