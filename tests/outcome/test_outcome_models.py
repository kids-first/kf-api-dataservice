from datetime import datetime
import uuid

from sqlalchemy.exc import IntegrityError

from dataservice.api.participant.models import Participant
from dataservice.api.outcome.models import Outcome
from dataservice.extensions import db
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test Outcome database model
    """

    def test_create(self):
        """
        Test create outcome
        """
        # Create and save participant
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id)
        db.session.add(p)
        db.session.commit()

        # Create outcomes
        data = {
            'vital_status': 'Alive',
            'disease_related': False,
            'age_at_event_days': 120,
            'participant_id': p.kf_id
        }
        dt = datetime.now()
        o1 = Outcome(**data)
        db.session.add(o1)
        data['vital_status'] = 'Dead'
        data['disease_related'] = 'True'
        o2 = Outcome(**data)
        db.session.add(o2)
        db.session.commit()

        self.assertEqual(Outcome.query.count(), 2)
        new_outcome = Outcome.query.all()[1]
        self.assertGreater(new_outcome.created_at, dt)
        self.assertGreater(new_outcome.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_outcome.uuid)), uuid.UUID)

        self.assertEqual(new_outcome.vital_status, data['vital_status'])
        self.assertEqual(new_outcome.disease_related,
                         data['disease_related'])

    def test_create_via_participant(self):
        """
        Test create outcomes via creation of participant
        """
        # Create two outcomes
        oc = ['Dead', 'Alive']
        o1 = Outcome(vital_status=oc[0])
        o2 = Outcome(vital_status=oc[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.outcomes.extend([o1, o2])
        db.session.add(p)
        db.session.commit()

        # Check outcomes were created
        self.assertEqual(Outcome.query.count(), 2)

        # Check Particpant has the outcomes
        for o in Participant.query.first().outcomes:
            self.assertIn(o.vital_status, oc)

        # Outcomes have the participant
        p = Participant.query.first()
        for o in Outcome.query.all():
            self.assertEqual(o.participant_id, p.kf_id)

    def test_find_outcome(self):
        """
        Test find one outcome
        """
        # Create two outcomes
        oc = ['Dead', 'Alive']
        o1 = Outcome(vital_status=oc[0])
        o2 = Outcome(vital_status=oc[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.outcomes.extend([o1, o2])
        db.session.add(p)
        db.session.commit()

        # Find outcome
        o = Outcome.query.filter_by(vital_status=oc[0]).one_or_none()
        self.assertEqual(o.vital_status, oc[0])

    def test_update_outcome(self):
        """
        Test update outcome
        """
        # Create two outcomes
        oc = ['Dead', 'Alive']
        o1 = Outcome(vital_status=oc[0])
        o2 = Outcome(vital_status=oc[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.outcomes.extend([o1, o2])
        db.session.add(p)
        db.session.commit()

        # Update and save
        o = Outcome.query.filter_by(vital_status=oc[0]).one_or_none()
        vital = 'Alive'
        o.outcome = vital
        db.session.commit()

        # Check updated values
        o = Outcome.query.filter_by(vital_status=vital).one_or_none()
        self.assertIsNot(o, None)

    def test_delete_outcome(self):
        """
        Test delete outcome
        """
        # Create two outcomes
        oc = ['Dead', 'Alive']
        o1 = Outcome(vital_status=oc[0])
        o2 = Outcome(vital_status=oc[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.outcomes.extend([o1, o2])
        db.session.add(p)
        db.session.commit()

        # Choose one and delete it
        o = Outcome.query.filter_by(vital_status=oc[0]).one_or_none()
        db.session.delete(o)
        db.session.commit()

        o = Outcome.query.filter_by(vital_status=oc[0]).one_or_none()
        self.assertIs(o, None)
        outcomes = [_o for _o in p.outcomes]
        self.assertNotIn(o, outcomes)

    def test_delete_outcome_via_participant(self):
        """
        Test delete related outcomes via deletion of participant
        """
        # Create two outcomes
        oc = ['Dead', 'Alive']
        o1 = Outcome(vital_status=oc[0])
        o2 = Outcome(vital_status=oc[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.outcomes.extend([o1, o2])
        db.session.add(p)
        db.session.commit()

        # Delete participant
        db.session.delete(p)
        db.session.commit()

        # Check that outcomes have been deleted
        o1 = Outcome.query.filter_by(vital_status=oc[0]).one_or_none()
        o2 = Outcome.query.filter_by(vital_status=oc[1]).one_or_none()
        self.assertIs(o1, None)
        self.assertIs(o2, None)

    def test_not_null_constraint(self):
        """
        Test that a outcome cannot be created without required
        parameters such as participant_id
        """
        # Create outcome
        data = {
            'vital_status': 'Alive',
            # non-existent required param: participant_id
        }
        o = Outcome(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(o))

    def test_foreign_key_constraint(self):
        """
        Test that a outcome cannot be created without an existing
        reference Participant. This checks foreign key constraint
        """
        # Create outcome
        data = {
            'vital_status': 'Alive',
            'participant_id': ''  # empty blank foreign key
        }
        o = Outcome(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(o))
