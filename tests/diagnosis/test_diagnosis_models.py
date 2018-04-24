from datetime import datetime
import uuid

from sqlalchemy.exc import IntegrityError

from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.extensions import db
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test Diagnosis database model
    """

    def test_create_and_find(self):
        """
        Test create diagnosis
        """
        diagnoses, kwarg_dict = self._create_diagnoses()

        dt = datetime.now()

        self.assertEqual(Diagnosis.query.count(), len(diagnoses))

        for k, kwargs in kwarg_dict.items():
            d = Diagnosis.query.filter_by(external_id=k).one()
            for key, value in kwargs.items():
                self.assertEqual(value, getattr(d, key))
            self.assertGreater(dt, d.created_at)
            self.assertGreater(dt, d.modified_at)
            self.assertIs(type(uuid.UUID(d.uuid)), uuid.UUID)

    def test_update_diagnosis(self):
        """
        Test update diagnosis
        """
        diagnoses, kwarg_dict = self._create_diagnoses()

        d = diagnoses[0]
        d.diagnosis = 'flu'
        db.session.commit()
        # Check updated values
        d = Diagnosis.query.get(d.kf_id)
        self.assertIs(d.diagnosis, 'flu')

    def test_delete_diagnosis(self):
        """
        Test delete diagnosis
        """
        diagnoses, kwarg_dict = self._create_diagnoses()

        p = Participant.query.first()
        kf_id = diagnoses[0].kf_id
        del p.diagnoses[0]
        db.session.commit()

        d = Diagnosis.query.get(kf_id)
        self.assertIs(d, None)
        diagnoses = [_d for _d in p.diagnoses]
        self.assertNotIn(d, diagnoses)

    def test_delete_diagnosis_via_participant(self):
        """
        Test delete related diagnoses via deletion of participant
        """
        diagnoses, kwarg_dict = self._create_diagnoses()

        p = Participant.query.first()
        db.session.delete(p)
        db.session.commit()

        # Check that diagnoses have been deleted
        self.assertEqual(0, Diagnosis.query.count())

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
        db.session.add(d)
        with self.assertRaises(IntegrityError):
            db.session.commit()

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
        db.session.add(d)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def _create_diagnosis(self, _id, participant_id=None):
        """
        Create diagnosis
        """
        kwargs = {
            'external_id': 'id_{}'.format(_id),
            'source_text_diagnosis': 'diagnosis {}'.format(_id),
            'age_at_event_days': 365,
            'diagnosis_category': 'cancer',
            'source_text_tumor_location': 'Brain',
            'mondo_id': 'DOID:8469',
            'uberon_id':'UBERON:0000955',
            'icd_id': 'J10.01'
        }
        if participant_id:
            kwargs['participant_id'] = participant_id
        return Diagnosis(**kwargs), kwargs

    def _create_diagnoses(self, total=2):
        """
        Create diagnoses and other requred entities
        """
        # Create study
        study = Study(external_id='phs001')

        # Create participant
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, is_proband=True,
                        study=study)
        db.session.add(p)
        db.session.commit()

        # Create diagnoses
        diagnoses = []
        kwarg_dict = {}
        for i in range(total):
            d, kwargs = self._create_diagnosis(i)
            kwarg_dict[d.external_id] = kwargs
            diagnoses.append(d)

        p.diagnoses.extend(diagnoses)

        db.session.commit()

        return diagnoses, kwarg_dict
