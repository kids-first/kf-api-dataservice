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
        """
        create a participant and sample and save to db
        returns participant_id and sample_id
        """
        participant_id ="Test_Subject_0"
        sample_id ="Test_Sample_0"
        data={
        'external_id':sample_id,
        'tissue_type':'Normal',
        'composition':'Test_comp_0',
        'anatomical_site':'Brain',
        'age_at_event_days':456,
        'tumor_descriptor':'Metastatic'
        }
        sample_0 = Sample(**data)
        participant_0 = Participant(external_id = participant_id, samples =[sample_0])
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
        s = Sample(external_id='Test_Sample_0', tissue_type='Normal', composition='Test_comp_0',
                   anatomical_site='Brain', age_at_event_days=456, tumor_descriptor='Metastatic', participant_id=p.kf_id)
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
        """
        create sample via participant
        """
        participant_id, sample_id= self.create_participant_sample()
        s = Sample.query.filter_by(external_id=sample_id).one_or_none()
        p = Participant.query.filter_by(external_id=participant_id).one_or_none()
        self.assertEqual(p.kf_id,s.participant_id)
        self.assertEqual(p.samples[0].external_id,s.external_id)


    def test_find_sampe(self):
        """
        test finding the sample with sample_id
        """
        participant_id, sample_id= self.create_participant_sample()
        
        # get sample
        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertEqual(s.external_id, "Test_Sample_0")
        self.assertEqual(s.tissue_type, "Normal")
        self.assertEqual(s.composition,"Test_comp_0")
        self.assertEqual(s.external_id,sample_id)

    def test_update_sample(self):
        """
        Test Updating sample 
        """
        participant_id, sample_id= self.create_participant_sample()
        # get sample
        s= Sample.query.filter_by(external_id=sample_id).one_or_none()

        s.tissue_type ="Tumor"
        # get sample
        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertEqual(s.tissue_type, 'Tumor')
        self.assertEqual(s.external_id,sample_id)

    def test_delete_sample(self):
        """
        Test Deleting Sample
        """
        participant_id, sample_id= self.create_participant_sample()
        #get Sample
        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        
        #Delete Sample
        db.session.delete(s)
        db.session.commit()

        s= Sample.query.filter_by(external_id=sample_id).one_or_none()
        self.assertIs(s,None)
        self.assertIsNone(Participant.query.filter_by(external_id=sample_id).one_or_none())

    def test_delete_sample_participant(self):
        """
        Test deleting sample via participant
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

    def test_not_null_constraint(self):
        """
        Test sample cannot be created with out required parameters such as participant_id
        """    
        # Create Sample
        sample_id = "Test_Sample_0"
    
        # With Missing Kf_id
        s = Sample(external_id='Test_Sample_0', tissue_type='Normal', composition='Test_comp_0',
                   anatomical_site='Brain', tumor_descriptor='Metastatic', age_at_event_days=456)

        #Add Sample to db
        self.assertRaises(IntegrityError, db.session.add(s))

    def test_foreign_key_constraint(self):

        """
        Test sample cannot be created with empty participant_id
    
        """    
        # Create Sample
        sample_id = "Test_Sample_0"
    
        # With Empty Kf_id
        s = Sample(external_id='Test_Sample_0', tissue_type='Normal', composition='Test_comp_0',
                   anatomical_site='Brain', age_at_event_days=456, tumor_descriptor='Metastatic', participant_id ='')

        #Add Sample to db
        self.assertRaises(IntegrityError, db.session.add(s))
    
    def test_one_to_many_relationship_create(self):
        """
        Test creating multiple samples to the the Participant 
        """
        #create a participant with a sample
        participant_id, sample_id= self.create_participant_sample()
        p = Participant.query.filter_by(external_id=participant_id).one_or_none()
        
        #adding another sample to participant
        s = Sample(external_id='Test_Sample_1', tissue_type='Normal', composition='Test_comp_1', 
                   anatomical_site='Brain', age_at_event_days=456, tumor_descriptor='Metastatic', participant_id =p.kf_id)
        
        db.session.add(s)
        db.session.commit()
        p = Participant.query.filter_by(external_id=participant_id).all()
        print(p[0].samples)
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(p[0].samples[0].external_id,'Test_Sample_0')
        self.assertEqual(p[0].samples[1].external_id,'Test_Sample_1')
        self.assertEqual(p[0].kf_id,s.participant_id)
        self.assertEqual(Sample.query.count(), 2)
    
    def test_one_to_many_realtionship_update(self):
        """
        Test Updating one of the samples in the participant
        """
        #create a participant with a sample
        participant_id, sample_id= self.create_participant_sample()
        p = Participant.query.filter_by(external_id=participant_id).one_or_none()
        
        #adding another sample to participant
        s = Sample(external_id='Test_Sample_1', tissue_type='Normal', composition='Test_comp_1', 
                   anatomical_site='Brain', age_at_event_days=456, tumor_descriptor='Metastatic', participant_id =p.kf_id)
        
        db.session.add(s)
        db.session.commit()

        #Get Sample and Person with multiple Entries
        p = Participant.query.filter_by(external_id=participant_id).all()
        s= Sample.query.filter_by(external_id='Test_Sample_1').one_or_none()
        print(s.tissue_type)
        #update one of the sample attribute
        s.tissue_type='Tumor'

        s= Sample.query.filter_by(external_id='Test_Sample_1').one_or_none()
        self.assertEqual(s.tissue_type, 'Tumor')
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(p[0].samples[1].external_id,'Test_Sample_1')
        self.assertEqual(Sample.query.count(), 2)

    def test_one_to_many_relationship_delete(self):
        """
        Test Deleting one of the samples 
        """
        #create a participant with a sample
        participant_id, sample_id= self.create_participant_sample()
        p = Participant.query.filter_by(external_id=participant_id).one_or_none()
        
        #adding another sample to participant
        s = Sample(external_id='Test_Sample_1', tissue_type='Normal', composition='Test_comp_1', 
                   anatomical_site='Brain', age_at_event_days=456, tumor_descriptor='Metastatic', participant_id =p.kf_id)
        
        db.session.add(s)
        db.session.commit()

        #Delete Sample
        db.session.delete(s)
        db.session.commit()
        self.assertEqual(Sample.query.count(), 1)
        