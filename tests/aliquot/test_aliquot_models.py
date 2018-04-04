from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.sample.models import Sample
from dataservice.api.aliquot.models import Aliquot
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def create_participant_sample_aliquot(self):
        """
        create a participant, sample, and aliquot save to db
        returns participant_id, sample_id, and aliquot_id
        """
        # Create study
        study = Study(external_id='phs001')

        dt = datetime.now()
        participant_id = "Test_Subject_0"
        sample_id = "Test_Sample_0"
        aliquot_id = "Test_Aliquot_0"
        sample_data =self._make_sample(external_id=sample_id)
        aliquot_data=self._make_aliquot(external_id=aliquot_id)
        aliquot_0 = Aliquot(**aliquot_data)
        sample_0 = Sample(**sample_data, aliquots=[aliquot_0])
        participant_0 = Participant(
            external_id=participant_id,
            is_proband=True,
            samples=[sample_0],
            study=study)
        db.session.add(participant_0)
        db.session.commit()
        return participant_id, sample_id, aliquot_id

    def test_create_aliquot_sample_participant(self):
        """
        Test creation of aliquot via sample and person
        """
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()
        s = Sample.query.filter_by(external_id=sample_id).one_or_none()
        p = Participant.query.filter_by(
            external_id=participant_id).one_or_none()
        a = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertEqual(p.kf_id, s.participant_id)
        self.assertEqual(p.samples[0].external_id, s.external_id)
        self.assertEqual(p.samples[0].aliquots[0].external_id, a.external_id)

    def test_create_aliquot(self):
        """
        Test creation of aliquot
        """
        dt = datetime.now()
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()
        self.assertEqual(Aliquot.query.count(), 1)
        new_aliquot = Aliquot.query.first()
        s = Sample.query.first()
        self.assertGreater(new_aliquot.created_at, dt)
        self.assertGreater(new_aliquot.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_aliquot.uuid)), uuid.UUID)
        self.assertEqual(new_aliquot.external_id, "Test_Aliquot_0")
        self.assertEqual(new_aliquot.shipment_origin, "CORIELL")
        self.assertEqual(new_aliquot.shipment_destination, "Broad Institute")
        self.assertEqual(new_aliquot.analyte_type, "DNA")
        self.assertGreaterEqual(new_aliquot.shipment_date, dt)
        self.assertEqual(new_aliquot.sample_id, s.kf_id)

    def test_find_aliquot(self):
        """
        test finding the aliquot with aliquot_id
        """
        dt = datetime.now()
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()

        # get aliquot
        a = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertEqual(a.external_id, "Test_Aliquot_0")
        self.assertEqual(a.shipment_origin, "CORIELL")
        self.assertEqual(a.shipment_destination, "Broad Institute")
        self.assertEqual(a.analyte_type, "DNA")
        self.assertGreaterEqual(a.shipment_date, dt)
        self.assertEqual(a.external_id, aliquot_id)

    def test_update_aliquot(self):
        """
        Test Updating aliquot
        """
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()
        # get aliquot
        a = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()

        a.analyte_type = "RNA"
        # get sample
        a = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertEqual(a.analyte_type, 'RNA')
        self.assertEqual(a.external_id, aliquot_id)

    def test_delete_aliquot(self):
        """
        Test Deleting Aliquot
        """
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()
        # get Aliquot
        a = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()

        # Delete Aliquot
        db.session.delete(a)
        db.session.commit()

        a = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertIs(a, None)
        self.assertIsNone(
            Sample.query.filter_by(
                external_id=aliquot_id).one_or_none())
        self.assertEqual(Sample.query.count(), 1)
        self.assertEqual(Participant.query.count(), 1)

    def test_delete_aliquot_sample_participant(self):
        """
        Test deleting aliquot via sample and participant
        """
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()

        # Delete Participant
        p = Participant.query.first()
        db.session.delete(p)
        db.session.commit()

        s = Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertIs(s, None)
        # Check no sample exists in participant
        self.assertIsNone(
            Participant.query.filter_by(
                external_id=sample_id).one_or_none())

        a = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertIs(a, None)

        # Check No aliquot exists in sample
        self.assertIsNone(
            Sample.query.filter_by(
                external_id=aliquot_id).one_or_none())

    def test_not_null_constraint(self):
        """
        Test aliquot cannot be created with out sample or participant
        """
        dt = datetime.now()
        # Create aliquot without sample kf_id
        aliquot_data=self._make_aliquot(external_id="Test_Aliquot_0")
        a = Aliquot(**aliquot_data)

        # Add Aliquot to db
        self.assertRaises(IntegrityError, db.session.add(a))

    def test_foreign_key_constraint(self):
        """
        Test aliquot cannot be created with empty sample_id

        """
        dt = datetime.now()
        # Create aliquot
        aliquot_data=self._make_aliquot(external_id="Test_Aliquot_0")
        a = Aliquot(**aliquot_data, sample_id='')

        # Add aliquot to db
        self.assertRaises(IntegrityError, db.session.add(a))

    def test_one_to_many_relationship_create(self):
        """
        Test creating multiple aliquots to the the Sample
        """
        dt = datetime.now()
        # create a participant with a sample and a aliquot
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()
        p = Participant.query.filter_by(
            external_id=participant_id).one_or_none()

        # adding another sample to participant
        sample_data =self._make_sample(external_id='Test_Sample_1')
        s = Sample(**sample_data,participant_id=p.kf_id)
        db.session.add(s)
        db.session.commit()

        # adding one aliquot to sample2
        aliquot_data=self._make_aliquot(external_id="Test_Aliquot_2")
        a = Aliquot(**aliquot_data, sample_id=s.kf_id)
        db.session.add(a)
        db.session.commit()

        # adding second aliquot to sample2
        aliquot_data=self._make_aliquot(external_id="Test_Aliquot_1")
        a = Aliquot(**aliquot_data, sample_id=s.kf_id)
        db.session.add(a)
        db.session.commit()

        # p-s1-a1
        # p-s2-a2,a3

        p = Participant.query.filter_by(external_id=participant_id).all()
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(p[0].samples[0].external_id, 'Test_Sample_0')
        self.assertEqual(p[0].samples[1].external_id, 'Test_Sample_1')

        s1 = Sample.query.filter_by(external_id=sample_id).all()
        s2 = Sample.query.filter_by(external_id=s.external_id).all()

        self.assertEqual(Sample.query.count(), 2)
        self.assertEqual(s1[0].aliquots[0].external_id, 'Test_Aliquot_0')
        self.assertEqual(s2[0].aliquots[0].external_id, 'Test_Aliquot_2')

        a1 = Aliquot.query.filter_by(external_id=aliquot_id).all()
        a2 = Aliquot.query.filter_by(external_id=a.external_id).all()

        self.assertEqual(Aliquot.query.count(), 3)
        self.assertEqual(p[0].kf_id, s.participant_id)

        self.assertEqual(s1[0].kf_id, a1[0].sample_id)
        self.assertEqual(s2[0].kf_id, a2[0].sample_id)

    def test_one_to_many_relationship_update(self):
        """
        Test updating one of the aliquot in samples
        """
        dt = datetime.now()
        # create a participant with a sample and a aliquot
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()
        p = Participant.query.filter_by(
            external_id=participant_id).one_or_none()

        # adding another sample to participant
        sample_data = self._make_sample(external_id='Test_Sample_1')
        s = Sample(**sample_data,participant_id=p.kf_id)
        db.session.add(s)
        db.session.commit()

        # adding one aliquot to sample2
        aliquot_data=self._make_aliquot(external_id="Test_Aliquot_2")
        a = Aliquot(**aliquot_data, sample_id=s.kf_id)
        db.session.add(a)
        db.session.commit()

        # adding second aliquot to sample2
        aliquot_data=self._make_aliquot(external_id="Test_Aliquot_1")
        a = Aliquot(**aliquot_data, sample_id=s.kf_id)
        db.session.add(a)
        db.session.commit()

        # p-s1-a1
        # p-s2-a2,a3
        # Get participant, samples and aliquots

        p = Participant.query.filter_by(external_id=participant_id).all()

        s1 = Sample.query.filter_by(external_id=sample_id).all()
        s2 = Sample.query.filter_by(external_id=s.external_id).all()

        a1 = Aliquot.query.filter_by(external_id=aliquot_id).all()
        a2 = Aliquot.query.filter_by(external_id=a.external_id).all()

        # update a1 and a2
        a1[0].analyte_type = 'RNA'
        a2[0].volume = 13.89
        db.session.commit()

        # get updated aliquots
        a1 = Aliquot.query.filter_by(external_id=aliquot_id).all()
        a2 = Aliquot.query.filter_by(external_id=a.external_id).all()
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(p[0].samples[0].external_id, 'Test_Sample_0')
        self.assertEqual(p[0].samples[1].external_id, 'Test_Sample_1')

        self.assertEqual(Sample.query.count(), 2)
        self.assertEqual(s1[0].aliquots[0].external_id, 'Test_Aliquot_0')
        self.assertEqual(s2[0].aliquots[0].external_id, 'Test_Aliquot_2')

        self.assertEqual(Aliquot.query.count(), 3)
        self.assertEqual(a1[0].analyte_type, 'RNA')
        self.assertEqual(a2[0].volume, 13.89)

    def test_one_to_many_relationship_delete(self):
        """
        Test deleting one of the aliquot in samples
        """
        dt = datetime.now()
        # create a participant with a sample and a aliquot
        (participant_id,
         sample_id,
         aliquot_id) = self.create_participant_sample_aliquot()
        p = Participant.query.filter_by(
            external_id=participant_id).one_or_none()

        # adding another sample to participant
        sample_data = self._make_sample(external_id='Test_Sample_1')
        s = Sample(**sample_data,participant_id=p.kf_id)

        db.session.add(s)
        db.session.commit()

        # adding one aliquot to sample2
        aliquot_data=self._make_aliquot(external_id='Test_Aliquot_2')
        a = Aliquot(**aliquot_data, sample_id=s.kf_id)
        db.session.add(a)
        db.session.commit()

        # adding second aliquot to sample2
        aliquot_data=self._make_aliquot(external_id='Test_Aliquot_1')
        a = Aliquot(**aliquot_data, sample_id=s.kf_id)
        db.session.add(a)
        db.session.commit()

        # p-s1-a1
        # p-s2-a2,a3
        # Get participant, samples and aliquots

        p = Participant.query.filter_by(external_id=participant_id).all()

        s1 = Sample.query.filter_by(external_id=sample_id).one_or_none()
        s2 = Sample.query.filter_by(external_id=s.external_id).one_or_none()

        a1 = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        a2 = Aliquot.query.filter_by(external_id=a.external_id).one_or_none()

        # delete a2
        db.session.delete(a2)
        db.session.commit()

        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(Sample.query.count(), 2)
        self.assertEqual(Aliquot.query.count(), 2)

    def _make_aliquot(self, external_id=None):
        '''
        Convenience method to create a aliquot with a given source name
        '''
        dt = datetime.now()
        body = {
            'external_id': external_id,
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Broad Institute',
            'analyte_type': 'DNA',
            'concentration': 100,
            'volume': 12.67,
            'shipment_date': dt
        }
        return body

    def _make_sample(self, external_id=None):
        '''
        Convenience method to create a sample with a given source name
        '''
        dt = datetime.now()
        body = {
            'external_id': external_id,
            'tissue_type': 'Normal',
            'composition': 'Test_comp_1',
            'anatomical_site': 'Brain',
            'age_at_event_days': 456,
            'tumor_descriptor': 'Metastatic'
        }
        return body
