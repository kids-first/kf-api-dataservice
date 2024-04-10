from sqlalchemy.exc import IntegrityError

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase
from unittest.mock import patch, Mock


class ModelTest(FlaskTestCase):
    """
    Test Study database model
    """

    def test_create_and_find(self):
        """
        Test create study
        """
        # Create participants and study
        participants, study, kwargs = self.create_study()

        # Check database
        # Counts
        self.assertEqual(1, Study.query.count())
        self.assertEqual(4, Participant.query.count())
        # Study content
        for k, v in kwargs.items():
            self.assertEqual(v, getattr(study, k))
        # Participant studies
        for p in participants:
            self.assertEqual(study.kf_id, p.study.kf_id)

    def test_parent_study_id(self):
        # Create participants and study
        participants, study, kwargs = self.create_study()

        # Test parent study ID
        kwargs = {
            'external_id': 'foo',
            'parent_study_id': study.kf_id,
            'name': 'study1',
        }
        study1 = Study(**kwargs)
        db.session.add(study1)
        db.session.commit()

    def test_bucket_service(self):
        """
        Test that a request is sent to create a new bucket
        """
        s = Study(external_id='phs002', short_code='KF-ST0')
        db.session.add(s)
        db.session.commit()
        assert self.bucket_service.post.call_count == 1

        headers = {'Authorization': 'Bearer test123'}
        self.bucket_service.post.assert_called_with('/buckets',
                                                    json={'study_id': s.kf_id},
                                                    headers=headers)

    def test_update(self):
        """
        Test update study
        """
        # Create participants and study
        participants, study, kwargs = self.create_study()

        # Add new participant to study
        p_new = Participant(external_id='Bart', is_proband=True,
                            study_id=study.kf_id)
        db.session.add(p_new)
        db.session.commit()

        # Check database
        self.assertEqual(5, len(Study.query.get(study.kf_id).participants))
        self.assertIn(p_new, Study.query.get(study.kf_id).participants)

        # Change participant's study
        s = Study(external_id='phs002', short_code='KF_ST0')
        p0 = participants[0]
        p0.study = s
        db.session.commit()

        # Check database
        self.assertEqual(p0.study.kf_id,
                         Study.query.filter_by(
                             external_id='phs002').one().kf_id)
        self.assertNotIn(p0, Study.query.get(study.kf_id).participants)

    def test_delete(self):
        """
        Test delete study
        """
        # Create participants and study
        participants, study, kwargs = self.create_study()

        # Delete study
        kf_id = study.kf_id
        db.session.delete(study)
        db.session.commit()

        # Check database
        self.assertEqual(None, Study.query.get(kf_id))
        self.assertEqual(0, Participant.query.count())

    def test_delete_relations(self):
        """
        Test delete study from Participant
        """
        # Create participants and study
        participants, study, kwargs = self.create_study()

        # Delete study from participant
        p0 = participants[0]
        del p0.study
        db.session.commit()

        # Check database
        self.assertNotIn(p0, Study.query.get(study.kf_id).participants)

    def test_foreign_key_constraint(self):
        """
        Test that a participant cannot be created without existing
        reference Study. This checks foreign key constraint
        """
        # Create participant
        p = Participant(external_id='Fred', is_proband=True)
        db.session.add(p)

        # Check for exception
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_not_null_constraint(self):
        """
        Test that a study cannot be created without required parameters

        study requires external_id, data_access_authority
        """
        # Create study
        data = {}
        db.session.add(Study(**data))

        # Check for exception
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Check database
        self.assertEqual(0, Study.query.count())

    def create_study(self):
        # Create participants
        names = ['Fred', 'Wilma', 'Pebbles', 'Dino']
        participants = [Participant(external_id=n, is_proband=True,)
                        for n in names]

        # Create study
        kwargs = {
            'attribution': ('https://dbgap.ncbi.nlm.nih.gov/'
                            'aa/wga.cgi?view_pdf&stacc=phs000178.v9.p8'),
            'external_id': 'phs001',
            'name': 'study1',
            'short_code': 'KF-ST1',
            'short_name': 'S1',
            'version': 'v1',
            'release_status': 'Pending'
        }
        study = Study(**kwargs)

        # Add participants to study
        study.participants.extend(participants)
        db.session.add(study)
        db.session.commit()

        return participants, study, kwargs
