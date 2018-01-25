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
    def create_sample_aliquot(self):
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
        }
        sample_0 = Sample(**data)
        participant_0 = Participant(external_id = participant_id, samples =[sample_0])
        db.session.add(participant_0)
        db.session.commit()
        return participant_id,sample_id