from datetime import datetime
import uuid

from sqlalchemy.exc import IntegrityError

from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.demographic.models import Demographic
from dataservice.extensions import db
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def test_create(self):
        """
        Test create demographic
        """
        study = Study(external_id='phs001')
        db.session.add(study)
        db.session.commit()

        # Create and save participant
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id,
                        is_proband=True, study_id=study.kf_id)
        db.session.add(p)
        db.session.commit()

        # Create and save demographic
        demo_id = 'demo_1'
        data = {
            'external_id': demo_id,
            'race': 'asian',
            'ethnicity': 'not hispanic',
            'gender': 'female',
            'participant_id': p.kf_id
        }
        dt = datetime.now()
        d = Demographic(**data)
        db.session.add(d)
        db.session.commit()

        # Check that demographic was created correctly
        self.assertEqual(Demographic.query.count(), 1)
        new_demographic = Demographic.query.first()
        self.assertGreater(new_demographic.created_at, dt)
        self.assertGreater(new_demographic.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_demographic.uuid)), uuid.UUID)

        self.assertEqual(new_demographic.external_id, data['external_id'])
        self.assertEqual(new_demographic.race, data['race'])
        self.assertEqual(new_demographic.ethnicity, data['ethnicity'])
        self.assertEqual(new_demographic.gender, data['gender'])
        self.assertEqual(new_demographic.participant_id, p.kf_id)

    def test_create_via_participant(self):
        """
        Test create of demographic via creation of participant
        """
        # Create and save demographic
        participant_id, demo_id = self._create_save_demographic()

        # Check foreign key
        d = Demographic.query.filter_by(external_id=demo_id).one_or_none()
        p = Participant.query.filter_by(external_id=participant_id).\
            one_or_none()
        self.assertEqual(p.kf_id, d.participant_id)
        self.assertEqual(p.demographic.external_id, d.external_id)

    def test_find_demographic(self):
        """
        Test find one demographic
        """
        # Create and save demographic
        participant_id, demo_id = self._create_save_demographic()

        # Find demographic
        d = Demographic.query.filter_by(external_id=demo_id).one_or_none()

        self.assertEqual(d.race, 'asian')
        self.assertEqual(d.gender, 'female')
        self.assertEqual(d.external_id, demo_id)

    def test_update_demographic(self):
        """
        Test update demographic
        """
        # Create and save demographic
        participant_id, demo_id = self._create_save_demographic()

        # Find demographic
        d = Demographic.query.filter_by(external_id=demo_id).one_or_none()

        # Update demographic
        d.race = 'african'
        d.gender = 'male'

        # Find demographic
        d = Demographic.query.filter_by(external_id=demo_id).one_or_none()

        self.assertEqual(d.race, 'african')
        self.assertEqual(d.gender, 'male')
        self.assertEqual(d.external_id, demo_id)

    def test_delete_demographic(self):
        """
        Test delete demographic
        """
        # Create and save demographic
        participant_id, demo_id = self._create_save_demographic()

        # Find demographic
        d = Demographic.query.filter_by(external_id=demo_id).one_or_none()

        # Delete demographic
        db.session.delete(d)
        db.session.commit()

        d = Demographic.query.filter_by(external_id=demo_id).one_or_none()
        self.assertIs(d, None)

        p = Participant.query.filter_by(external_id=participant_id).\
            one_or_none()
        self.assertIs(p.demographic, None)

    def test_delete_demographic_via_participant(self):
        """
        Test delete demographic via deletion of participant

        This tests the cascade delete functionality of the sqlalchemy model
        """
        # Create and save demographic
        participant_id, demo_id = self._create_save_demographic()

        # Delete participant
        p = Participant.query.first()
        db.session.delete(p)
        db.session.commit()

        d = Demographic.query.filter_by(external_id=demo_id).one_or_none()
        self.assertIs(d, None)

        p = Participant.query.filter_by(external_id=participant_id).\
            one_or_none()
        self.assertIs(p, None)

    def test_not_null_constraint(self):
        """
        Test that a demographic cannot be created without required
        parameters such as participant_id
        """
        # Create demographic
        demo_id = 'demo_1'
        data = {
            'external_id': demo_id,
            'race': 'asian',
            'ethnicity': 'not hispanic',
            'gender': 'female'
            # non-existent required param: participant_id
        }
        d = Demographic(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(d))

    def test_foreign_key_constraint(self):
        """
        Test that a demographic cannot be created without an existing
        reference Participant. This checks foreign key constraint
        """
        # Create demographic
        demo_id = 'demo_1'
        data = {
            'external_id': demo_id,
            'race': 'asian',
            'ethnicity': 'not hispanic',
            'gender': 'female',
            'participant_id': ''  # empty blank foreign key
        }
        d = Demographic(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(d))

    def test_one_to_one(self):
        """
        Test a participant can only have one demographic.

        This checks foreign key unique constraint
        """
        # Create and save demographic
        participant_id, demo_id = self._create_save_demographic()

        # Create second demographic
        d = Demographic(external_id='demo_2', participant_id=participant_id)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(d))

    def test_get_participant_demographic(self):
        """
        Test get demographic via the participant
        """
        # Create and save demographic
        participant_id, demo_id = self._create_save_demographic()

        p = Participant.query.filter_by(external_id=participant_id).\
            one_or_none()

        self.assertEqual(p.demographic.external_id, demo_id)

    def _create_save_demographic(self):
        """
        Create and save demographic

        Create a participant
        Create a demographic and add it to participant as kwarg
        Save participant
        """
        # Create study
        study = Study(external_id='phs001')
        db.session.add(study)
        db.session.commit()

        # Create demographic
        demo_id = 'demo_1'
        data = {
            'external_id': demo_id,
            'race': 'asian',
            'ethnicity': 'not hispanic',
            'gender': 'female'
        }
        d = Demographic(**data)

        # Create and save participant
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, is_proband=True,
                        demographic=d, study_id=study.kf_id)
        db.session.add(p)
        db.session.commit()

        return participant_id, demo_id
