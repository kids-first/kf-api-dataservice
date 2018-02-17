from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def _create_participant(self, external_id="Test_Participant_0"):
        """
        Create participant with external id
        """
        s = Study(external_id='phs001')
        p = Participant(external_id=external_id, family_id="Test_family_id_0",
                        is_proband=False, consent_type="GRU-IRB")
        s.participants.append(p)
        db.session.add(s)
        db.session.commit()
        return p

    def _get_participant(self, kf_id):
        """
        Get participant by kids first id
        """
        return Participant.query.filter_by(kf_id=kf_id).one_or_none()

    def test_create_participant(self):
        """
        Test creation of participant
        """
        dt = datetime.now()

        self._create_participant('Test_Participant_0')

        self.assertEqual(Participant.query.count(), 1)
        new_participant = Participant.query.first()
        self.assertGreater(new_participant.created_at, dt)
        self.assertGreater(new_participant.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_participant.uuid)), uuid.UUID)
        self.assertEqual(new_participant.external_id, "Test_Participant_0")
        self.assertEqual(new_participant.family_id, "Test_family_id_0")
        self.assertEqual(new_participant.is_proband,False)

    def test_get_participant(self):
        """
        Test retrieving a participant
        """
        participant = self._create_participant('Test_Participant_0')
        kf_id = participant.kf_id

        participant = self._get_participant(kf_id)
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(participant.external_id, "Test_Participant_0")
        self.assertEqual(participant.is_proband,False)
        self.assertEqual(participant.kf_id, kf_id)

    def test_participant_not_found(self):
        """
        Test retrieving a participant that does not exist
        """
        participant = self._get_participant("non_existent_id")
        self.assertEqual(participant, None)

    def test_update_participant(self):
        """
        Test updating a participant
        """
        participant = self._create_participant('Test_Participant_0')
        kf_id = participant.kf_id

        participant = self._get_participant(kf_id)
        new_name = "Updated-{}".format(participant.external_id)
        participant.external_id = new_name
        participant.consent_type = 'GRU-COL'
        db.session.commit()

        participant = self._get_participant(kf_id)
        self.assertEqual(participant.external_id, new_name)
        self.assertEqual(participant.consent_type, 'GRU-COL')
        self.assertEqual(participant.kf_id, kf_id)

    def test_delete_participant(self):
        """
        Test deleting a participant
        """
        participant = self._create_participant('Test_Participant_0')
        kf_id = participant.kf_id

        participant = self._get_participant(kf_id)
        db.session.delete(participant)
        db.session.commit()

        participant = self._get_participant(kf_id)
        self.assertEqual(participant, None)
