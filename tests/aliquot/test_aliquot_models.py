from datetime import datetime
import uuid

from dataservice.extensions import db
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
        dt = datetime.now()
        participant_id ="Test_Subject_0"
        sample_id ="Test_Sample_0"
        aliquot_id ="Test_Aliquot_0"
        sample_data={
        'external_id':sample_id,
        'tissue_type':'Normal',
        'composition':'Test_comp_0',
        'anatomical_site':'Brain',
        'age_at_event_days':456,
        'tumor_descriptor':'Metastatic'
        }
        aliquot_data={
        'external_id':aliquot_id,
        'shipment_origin':'CORIELL',
        'shipment_destination':'Broad Institute',
        'analyte_type':'DNA',
        'concentration':100,
        'volume':12.67,
        'shipment_date':dt
        }
        aliquot_0 = Aliquot(**aliquot_data)
        print(aliquot_0)
        sample_0 = Sample(**sample_data, aliquots=[aliquot_0])
        print(sample_0.aliquots)
        participant_0 = Participant(external_id = participant_id, samples =[sample_0])
        print(participant_0)
        db.session.add(participant_0)
        db.session.commit()
        return participant_id,sample_id,aliquot_id

    def test_create_aliquot_sample_participant(self):
        """
        Test creation of aliquot via sample and person
        """
        participant_id, sample_id, aliquot_id=self.create_participant_sample_aliquot()
        s = Sample.query.filter_by(external_id=sample_id).one_or_none()
        p = Participant.query.filter_by(external_id=participant_id).one_or_none()
        a = Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertEqual(p.kf_id,s.participant_id)
        self.assertEqual(p.samples[0].external_id,s.external_id)
        self.assertEqual(p.samples[0].aliquots[0].external_id,a.external_id)

    def test_create_aliquot(self):
        """
        Test creation of aliquot
        """
        dt = datetime.now()
        participant_id ="Test_Subject_0"
        # creating participant
        p = Participant(external_id = participant_id)
        db.session.add(p)
        db.session.commit()

        #Creating Sample
        s = Sample(external_id='Test_Sample_0', tissue_type='Normal', composition='Test_comp_0',
                   anatomical_site='Brain', age_at_event_days=456, participant_id =p.kf_id)
        db.session.add(s)
        db.session.commit()

        #creating aliquot
        aliquot_data={
        'external_id':'Test_Aliquot_0',
        'shipment_origin':'CORIELL',
        'shipment_destination':'Broad Institute',
        'analyte_type':'DNA',
        'concentration':100,
        'volume':12.67,
        'shipment_date':dt
        }
        a = Aliquot(**aliquot_data, sample_id = s.kf_id)
        db.session.add(a)
        db.session.commit()

        self.assertEqual(Aliquot.query.count(), 1)
        new_aliquot = Aliquot.query.first()
        self.assertGreater(new_aliquot.created_at, dt)
        self.assertGreater(new_aliquot.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_aliquot.uuid)), uuid.UUID)
        self.assertEqual(new_aliquot.external_id, "Test_Aliquot_0")
        self.assertEqual(new_aliquot.shipment_origin, "CORIELL")
        self.assertEqual(new_aliquot.shipment_destination,"Broad Institute")
        self.assertEqual(new_aliquot.analyte_type,"DNA")
        self.assertGreaterEqual(new_aliquot.shipment_date,dt)
        self.assertEqual(new_aliquot.sample_id,s.kf_id)

    def test_find_aliquot(self):
        """
        test finding the aliquot with aliquot_id
        """
        dt = datetime.now()
        participant_id, sample_id, aliquot_id= self.create_participant_sample_aliquot()
        
        # get aliquot
        a= Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertEqual(a.external_id, "Test_Aliquot_0")
        self.assertEqual(a.shipment_origin, "CORIELL")
        self.assertEqual(a.shipment_destination,"Broad Institute")
        self.assertEqual(a.analyte_type,"DNA")
        self.assertGreaterEqual(a.shipment_date,dt)
        self.assertEqual(a.external_id,aliquot_id)

    def test_update_aliquot(self):
        """
        Test Updating aliquot 
        """
        participant_id, sample_id, aliquot_id= self.create_participant_sample_aliquot()
        # get aliquot
        a= Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()

        a.analyte_type ="RNA"
        # get sample
        a= Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertEqual(a.analyte_type, 'RNA')
        self.assertEqual(a.external_id,aliquot_id)

    def test_delete_aliquot(self):
        """
        Test Deleting Aliquot
        """
        participant_id, sample_id, aliquot_id= self.create_participant_sample_aliquot()
        #get Aliquot
        a= Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        
        #Delete Aliquot
        db.session.delete(a)
        db.session.commit()

        a= Aliquot.query.filter_by(external_id=aliquot_id).one_or_none()
        self.assertIs(a,None)
        self.assertIsNone(Sample.query.filter_by(external_id=aliquot_id).one_or_none())
        self.assertEqual(Participant.query.count(),1)

    def test_delete_aliquot_sample_participant(self):
        """
        Test deleting aliquot via sample and participant
        """

        participant_id, sample_id= self.create_participant_sample()

        #Delete Participant
        p = Participant.query.first()
        db.session.delete(p)
        db.session.commit()

        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertIs(s,None)
        #Check no sample exists in participant
        self.assertIsNone(Participant.query.filter_by(external_id=sample_id).one_or_none())


