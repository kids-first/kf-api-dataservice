from datetime import datetime
import uuid

from sqlalchemy.exc import IntegrityError

from dataservice.api.participant.models import Participant
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.extensions import db
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test Diagnosis database model
    """

    def test_create(self):
        """
        Test create diagnosis
        """
        # Create and save participant
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id)
        db.session.add(p)
        db.session.commit()

        # Create diagnoses
        data = {
            'external_id': 'diag_1',
            'diagnosis': 'cold',
            'age_at_event_days': 120,
            'participant_id': p.kf_id
        }
        dt = datetime.now()
        d1 = Diagnosis(**data)
        db.session.add(d1)
        data['external_id'] = 'diag_2'
        data['diagnosis'] = 'flu'
        d2 = Diagnosis(**data)
        db.session.add(d2)
        db.session.commit()

        self.assertEqual(Diagnosis.query.count(), 2)
        new_diagnosis = Diagnosis.query.all()[1]
        self.assertGreater(new_diagnosis.created_at, dt)
        self.assertGreater(new_diagnosis.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_diagnosis.uuid)), uuid.UUID)

        self.assertEqual(new_diagnosis.external_id, data['external_id'])
        self.assertEqual(new_diagnosis.diagnosis,
                         data['diagnosis'])

    def test_create_via_participant(self):
        """
        Test create diagnoses via creation of participant
        """
        # Create two diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(diagnosis=pd[0])
        d2 = Diagnosis(diagnosis=pd[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.diagnoses.extend([d1, d2])
        db.session.add(p)
        db.session.commit()

        # Check diagnoses were created
        self.assertEqual(Diagnosis.query.count(), 2)

        # Check Particpant has the diagnoses
        for d in Participant.query.first().diagnoses:
            self.assertIn(d.diagnosis, pd)

        # Diagnoses have the participant
        p = Participant.query.first()
        for d in Diagnosis.query.all():
            self.assertEqual(d.participant_id, p.kf_id)

    def test_find_diagnosis(self):
        """
        Test find one diagnosis
        """
        # Create two diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(diagnosis=pd[0])
        d2 = Diagnosis(diagnosis=pd[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.diagnoses.extend([d1, d2])
        db.session.add(p)
        db.session.commit()

        # Find diagnosis
        d = Diagnosis.query.\
            filter_by(diagnosis=pd[0]).one_or_none()
        self.assertEqual(d.diagnosis, pd[0])

    def test_update_diagnosis(self):
        """
        Test update diagnosis
        """
        # Create two diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(diagnosis=pd[0])
        d2 = Diagnosis(diagnosis=pd[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.diagnoses.extend([d1, d2])
        db.session.add(p)
        db.session.commit()

        # Update and save
        d = Diagnosis.query.filter_by(diagnosis=pd[0]).one_or_none()
        diag = 'west nile'
        d.diagnosis = diag
        db.session.commit()

        # Check updated values
        d = Diagnosis.query.filter_by(diagnosis=diag).one_or_none()
        self.assertIsNot(d, None)

    def test_delete_diagnosis(self):
        """
        Test delete diagnosis
        """
        # Create two diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(diagnosis=pd[0])
        d2 = Diagnosis(diagnosis=pd[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.diagnoses.extend([d1, d2])
        db.session.add(p)
        db.session.commit()

        # Choose one and delete it
        d = Diagnosis.query.filter_by(diagnosis=pd[0]).one_or_none()
        db.session.delete(d)
        db.session.commit()

        d = Diagnosis.query.filter_by(diagnosis=pd[0]).one_or_none()
        self.assertIs(d, None)
        diagnoses = [_d for _d in p.diagnoses]
        self.assertNotIn(d, diagnoses)

    def test_delete_diagnosis_via_participant(self):
        """
        Test delete related diagnoses via deletion of participant
        """
        # Create two diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(diagnosis=pd[0])
        d2 = Diagnosis(diagnosis=pd[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.diagnoses.extend([d1, d2])
        db.session.add(p)
        db.session.commit()

        # Delete participant
        db.session.delete(p)
        db.session.commit()

        # Check that diagnoses have been deleted
        d1 = Diagnosis.query.filter_by(diagnosis=pd[0]).one_or_none()
        d2 = Diagnosis.query.filter_by(diagnosis=pd[1]).one_or_none()
        self.assertIs(d1, None)
        self.assertIs(d2, None)

    def test_not_null_constraint(self):
        """
        Test that a diagnosis cannot be created without required
        parameters such as participant_id
        """
        # Create diagnosis
        data = {
            'external_id': 'd1',
            # non-existent required param: participant_id
        }
        d = Diagnosis(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(d))

    def test_foreign_key_constraint(self):
        """
        Test that a diagnosis cannot be created without an existing
        reference Participant. This checks foreign key constraint
        """
        # Create diagnosis
        data = {
            'external_id': 'd1',
            'participant_id': ''  # empty blank foreign key
        }
        d = Diagnosis(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(d))
