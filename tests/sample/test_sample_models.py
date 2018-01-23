from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.sample.models import Sample
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError

class ModelTest(FlaskTestCase):
    """
    Test database model
    """
    def create_participant_sample(self):
        participant_id ="Test_Subject_0"
        sample_id ="Test_Sample_0"
        data={
        'external_id': sample_id,
        'tissue_type': 'Normal',
        'composition': 'Test_comp_0',
        }
        sample_0 = Sample(**data)
        participant_0 = Participant(external_id = participant_id,sample =sample_0)
        db.session.add(participant_0)
        db.session.commit()
        return participant_id,sample_id
  
    def test_create_sample(self):
        """
        Test creation of sample
        """
        dt = datetime.now()
        participant_id ="Test_Subject_0"
        # creating participant
        p = Participant(external_id = participant_id)
        db.session.add(p)
        db.session.commit()

        #Creating Sample
        s = Sample(external_id='Test_Sample_0',tissue_type='Normal',composition='Test_comp_0',participant_id =p.kf_id)
        db.session.add(s)
        db.session.commit()


        self.assertEqual(Sample.query.count(), 1)
        new_sample = Sample.query.first()
        self.assertGreater(new_sample.created_at, dt)
        self.assertGreater(new_sample.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_sample.uuid)), uuid.UUID)
        self.assertEqual(new_sample.external_id, "Test_Sample_0")
        self.assertEqual(new_sample.tissue_type, "Normal")
        self.assertEqual(new_sample.composition,"Test_comp_0")
        self.assertEqual(new_sample.participant_id,p.kf_id)

    
    def test_sample_participant_relation(self):
        participant_id, sample_id= self.create_participant_sample()
        s = Sample.query.filter_by(external_id=sample_id).one_or_none()
        p = Participant.query.filter_by(external_id=participant_id).one_or_none()
        self.assertEqual(p.kf_id,s.participant_id)
        self.assertEqual(p.sample.external_id,s.external_id)


    def test_find_sampe(self):
        participant_id, sample_id= self.create_participant_sample()
        
        # get sample
        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertEqual(s.external_id, "Test_Sample_0")
        self.assertEqual(s.tissue_type, "Normal")
        self.assertEqual(s.composition,"Test_comp_0")
        self.assertEqual(s.external_id,sample_id)

    def test_update_sample(self):
        participant_id, sample_id= self.create_participant_sample()
         # get sample
        s= Sample.query.filter_by(external_id=sample_id).one_or_none()

        s.tissue_type ="Tumor"
          # get sample
        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertEqual(s.tissue_type, 'Tumor')
        self.assertEqual(s.external_id,sample_id)

    def test_delete_sample(self):
        participant_id, sample_id= self.create_participant_sample()
        #get Sample
        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        
        #Delete Sample
        db.session.delete(s)
        db.session.commit()

        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertIs(s,None)

        #p= Participant.query.filter_by(external_id=sample_id).one_or_none()
        self.assertIsNone(Participant.query.filter_by(external_id=sample_id).one_or_none())

    def test_delete_sample_participant(self):

        participant_id, sample_id= self.create_participant_sample()

        #Delete Participant
        p = Participant.query.first()
        db.session.delete(p)
        db.session.commit()

        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertIs(s,None)
 
        self.assertIsNone(Participant.query.filter_by(external_id=sample_id).one_or_none())

    def test_not_null_constraint(self):

    
        """
        Test sample cannot be created with out required parameters such as participant_id
    
        """    

        # Create Sample
        sample_id = "Test_Sample_0"
    
        # With Missing Kf_id
        s = Sample(external_id='Test_Sample_0',tissue_type='Normal',composition='Test_comp_0')

        #Add Sample to db
        self.assertRaises(IntegrityError, db.session.add(s))

    def test_foreign_key_constraint(self):

    
        """
        Test sample cannot be created with out required parameters such as participant_id
    
        """    

        # Create Sample
        sample_id = "Test_Sample_0"
    
        # With Empty Kf_id
        s = Sample(external_id='Test_Sample_0',tissue_type='Normal',composition='Test_comp_0',participant_id ='')

        #Add Sample to db
        self.assertRaises(IntegrityError, db.session.add(s))
        
    