from datetime import datetime
import uuid

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
        # Create diagnoses
        data = {
            'external_id': 'diag_1',
            'primary_diagnosis': 'cold',
            'progression_or_recurence': 'yes',
            'days_to_last_followup': 120
        }
        dt = datetime.now()
        d1 = Diagnosis(**data)
        db.session.add(d1)
        data['external_id'] = 'diag_2'
        data['primary_diagnosis'] = 'flu'
        d2 = Diagnosis(**data)
        db.session.add(d2)
        db.session.commit()

        self.assertEqual(Diagnosis.query.count(), 2)
        new_diagnosis = Diagnosis.query.all()[1]
        self.assertGreater(new_diagnosis.created_at, dt)
        self.assertGreater(new_diagnosis.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_diagnosis.uuid)), uuid.UUID)

        self.assertEqual(new_diagnosis.external_id, data['external_id'])
        self.assertEqual(new_diagnosis.primary_diagnosis,
                         data['primary_diagnosis'])
        self.assertEqual(new_diagnosis.progression_or_recurence,
                         data['progression_or_recurence'])

    def test_create_via_participant(self):
        """
        Test create diagnoses via creation of participant
        """
        # Create two diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(primary_diagnosis=pd[0])
        d2 = Diagnosis(primary_diagnosis=pd[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.diagnoses.extend([d1, d2])
        db.session.add(p)
        db.session.commit()

        # Check diagnoses were created
        self.assertEqual(Diagnosis.query.count(), 2)

        # Check Particpant has the diagnoses
        for d in Participant.query.first().diagnoses:
            self.assertIn(d.primary_diagnosis, pd)

        # Diagnoses have the participant
        p = Participant.query.first()
        for d in Diagnosis.query.all():
            participants = [_p for _p in d.participants]
            self.assertEqual(len(participants), 1)
            self.assertEqual(participants[0].kf_id, p.kf_id)

    def test_find_diagnosis(self):
        """
        Test find one diagnosis
        """
        # Create diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(primary_diagnosis=pd[0])
        d2 = Diagnosis(primary_diagnosis=pd[1])

        # Add and save to db
        db.session.add(d1)
        db.session.add(d2)
        db.session.commit()

        # Find diagnosis
        d = Diagnosis.query.\
            filter_by(primary_diagnosis=pd[0]).one_or_none()
        self.assertEqual(d.primary_diagnosis, pd[0])

    def test_update_diagnosis(self):
        """
        Test update diagnosis
        """
        # Create diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(primary_diagnosis=pd[0])
        d2 = Diagnosis(primary_diagnosis=pd[1])

        # Add and save to db
        db.session.add(d1)
        db.session.add(d2)
        db.session.commit()

        # Update and save
        d = Diagnosis.query.filter_by(primary_diagnosis=pd[0]).one_or_none()
        pr = 'yes'
        d.progression_or_recurence = pr
        db.session.commit()

        # Check updated values
        d = Diagnosis.query.filter_by(primary_diagnosis=pd[0]).one_or_none()
        self.assertEqual(d.progression_or_recurence, pr)

    def test_delete_diagnosis(self):
        """
        Test delete diagnosis
        """
        # Create diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(primary_diagnosis=pd[0])
        d2 = Diagnosis(primary_diagnosis=pd[1])

        # Add and save to db
        db.session.add(d1)
        db.session.add(d2)
        db.session.commit()

        # Choose one and delete it
        d = Diagnosis.query.filter_by(primary_diagnosis=pd[0]).one_or_none()
        db.session.delete(d)
        db.session.commit()

        d = Diagnosis.query.filter_by(primary_diagnosis=pd[0]).one_or_none()
        self.assertIs(d, None)

    def test_delete_diagnosis_via_participant(self):
        """
        Test delete related diagnoses via deletion of participant
        """
        # Create two diagnoses
        pd = ['cold', 'flu']
        d1 = Diagnosis(primary_diagnosis=pd[0])
        d2 = Diagnosis(primary_diagnosis=pd[1])

        # Create participants
        p1 = Participant(external_id='p1')
        p2 = Participant(external_id='p2')

        # Add both diagnoses to first participant
        p1.diagnoses.extend([d1, d2])
        db.session.add(p1)

        # Add one diagnoses to second participant and save
        p2.diagnoses.append(d1)

        db.session.commit()

        # Check that diagnosis 1 is part of both participants
        d1 = Diagnosis.query.filter_by(primary_diagnosis=pd[0]).one()
        d1_partipants = [p for p in d1.participants]
        self.assertEqual(len(d1_partipants), 2)

        # Delete first participant
        db.session.delete(p1)
        db.session.commit()

        # Check that diagnosis 1 is part of only participant 2
        d1 = Diagnosis.query.filter_by(primary_diagnosis=pd[0]).one()
        d1_partipants = [p for p in d1.participants]
        self.assertEqual(len(d1_partipants), 1)
        self.assertEqual(d1_partipants[0].external_id, p2.external_id)
