from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def create_participant_biospecimen(self):
        """
        create a participant and biospecimen and save to db
        returns participant_id and biospecimen_id
        """
        participant_id = "Test_Subject_0"
        sample_id = "Test_Sample_0"
        aliquot_id = "Test_aliquot_0"
        data = self._make_biospecimen(external_sample_id=sample_id,
                                      external_aliquot_id=aliquot_id)
        ids = self.create_seqexp()
        biospecimen_0 = Biospecimen(**data,
                                    sequencing_center_id=\
                                    ids['sequencing_center_id'])
        participant_0 = Participant(
            external_id=participant_id,
            is_proband=True,
            biospecimens=[biospecimen_0])

        study = Study(external_id='phs001')
        study.participants.append(participant_0)

        db.session.add(study)
        db.session.commit()
        return participant_id, sample_id, aliquot_id

    def test_create_and_find_biospecimen(self):
        """
        Test creation of biospecimen
        """
        study = Study(external_id='phs001')
        db.session.add(study)
        db.session.commit()

        dt = datetime.now()
        participant_id = "Test_Subject_0"
        # creating participant
        p = Participant(external_id=participant_id, is_proband=True,
                        study_id=study.kf_id)
        db.session.add(p)
        db.session.commit()

        # Creating Biospecimen
        sample_id = "Test_Sample_0"
        aliquot_id = "Test_Aliquot_0"
        data = self._make_biospecimen(external_sample_id=sample_id,
                                      external_aliquot_id=aliquot_id)

        ids = self.create_seqexp()
        s = Biospecimen(**data, participant_id=p.kf_id,
                        sequencing_center_id=ids['sequencing_center_id'])
        db.session.add(s)
        db.session.commit()

        self.assertEqual(Biospecimen.query.count(), 1)
        bs = Biospecimen.query.first()
        for key, value in data.items():
            self.assertEqual(value, getattr(bs, key))
        self.assertGreater(bs.created_at, dt)
        self.assertGreater(bs.modified_at, dt)
        self.assertIs(type(uuid.UUID(bs.uuid)), uuid.UUID)

    def test_biospecimen_participant_relation(self):
        """
        create biospecimen via participant
        """
        (participant_id,
        sample_id,
        aliquot_id) = self.create_participant_biospecimen()
        s = Biospecimen.query.filter_by(external_sample_id=sample_id).\
            one_or_none()
        p = Participant.query.filter_by(
            external_id=participant_id).one_or_none()
        self.assertEqual(p.kf_id, s.participant_id)
        self.assertEqual(p.biospecimens[0].external_sample_id,
                         s.external_sample_id)

    def test_update_biospecimen(self):
        """
        Test Updating biospecimen
        """
        (participant_id,
        sample_id,
        aliquot_id) = self.create_participant_biospecimen()
        # Get Biospecimen
        s = Biospecimen.query.filter_by(external_sample_id=sample_id).\
            one_or_none()

        s.source_text_tissue_type = "Tumor"
        # get biospecimen
        s = Biospecimen.query.filter_by(external_sample_id=sample_id).\
           one_or_none()
        self.assertEqual(s.source_text_tissue_type, 'Tumor')
        self.assertEqual(s.external_sample_id, sample_id)

    def test_delete_biospecimen(self):
        """
        Test Deleting Biospecimen
        """
        (participant_id,
        sample_id,
        aliquot_id) = self.create_participant_biospecimen()
        # Get Biospecimen
        s = Biospecimen.query.filter_by(external_sample_id=sample_id).\
            one_or_none()

        # Delete Biospecimen
        db.session.delete(s)
        db.session.commit()

        s = Biospecimen.query.filter_by(external_sample_id=sample_id).\
            one_or_none()
        self.assertIs(s, None)
        self.assertIsNone(
            Participant.query.filter_by(
                external_id=sample_id).one_or_none())

    def test_delete_biospecimen_participant(self):
        """
        Test deleting biospecimen via participant
        """

        (participant_id,
        sample_id,
        aliquot_id) = self.create_participant_biospecimen()

        # Delete Participant
        p = Participant.query.first()
        db.session.delete(p)
        db.session.commit()

        # Get Biospecimen
        s = Biospecimen.query.filter_by(external_sample_id=sample_id).\
            one_or_none()
        self.assertIs(s, None)
        # Check no biospecimen exists in participant
        self.assertIsNone(
            Participant.query.filter_by(
                external_id=sample_id).one_or_none())

    def test_not_null_constraint(self):
        """
        Test biospecimen cannot be created with out required parameters
        such as participant_id
        """
        # Create Biospecimen
        sample_id = "Test_Sample_0"

        # With Missing Kf_id
        data = self._make_biospecimen(external_sample_id=sample_id)
        s = Biospecimen(**data)

        # Add Biospecimen to db
        self.assertRaises(IntegrityError, db.session.add(s))

    def test_foreign_key_constraint(self):
        """
        Test biospecimen cannot be created with empty participant_id

        """
        # Create Biospecimen
        biospecimen_id = "Test_Sample_0"

        # With Empty Kf_id
        data = self._make_biospecimen(external_sample_id=biospecimen_id)
        s = Biospecimen(**data, participant_id='')

        # Add Biospecimen to db
        self.assertRaises(IntegrityError, db.session.add(s))

    def test_one_to_many_relationship_create(self):
        """
        Test creating multiple biospecimens to the the Participant
        """
        # create a participant with a biospecimen
        (participant_id,
        sample_id,
        aliquot_id) = self.create_participant_biospecimen()
        p = Participant.query.filter_by(
            external_id=participant_id).one_or_none()

        # adding another biospecimen to participant
        data = self._make_biospecimen(external_sample_id='Test_Sample_1',
                                      external_aliquot_id='Test_Aliquot_id')

        ids = self.create_seqexp()
        s = Biospecimen(**data, participant_id=p.kf_id,
                        sequencing_center_id=ids['sequencing_center_id'])

        db.session.add(s)
        db.session.commit()
        p = Participant.query.filter_by(external_id=participant_id).all()
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(p[0].biospecimens[0].external_sample_id,
                         'Test_Sample_0')
        self.assertEqual(p[0].biospecimens[1].external_sample_id,
                         'Test_Sample_1')
        self.assertEqual(p[0].kf_id, s.participant_id)
        self.assertEqual(Biospecimen.query.count(), 2)

    def test_one_to_many_realtionship_update(self):
        """
        Test Updating one of the biospecimens in the participant
        """
        # create a participant with a biospecimen
        (participant_id,
        sample_id,
        aliquot_id) = self.create_participant_biospecimen()
        # Get Participant
        p = Participant.query.filter_by(
            external_id=participant_id).one_or_none()

        # adding another biospecimen to participant
        data = self._make_biospecimen(external_sample_id='Test_Sample_1',
                                      external_aliquot_id='Test_Aliquot_1')

        ids = self.create_seqexp()
        s = Biospecimen(**data, participant_id=p.kf_id,
                        sequencing_center_id=ids['sequencing_center_id'])

        db.session.add(s)
        db.session.commit()

        # Get Biospecimen and Person with multiple Entries
        p = Participant.query.filter_by(external_id=participant_id).all()
        s = Biospecimen.query.filter_by(external_sample_id='Test_Sample_1').\
           one_or_none()

        # update one of the biospecimen attribute
        s.source_text_tissue_type = 'Tumor'

        s = Biospecimen.query.filter_by(external_sample_id='Test_Sample_1').\
            one_or_none()
        self.assertEqual(s.source_text_tissue_type, 'Tumor')
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(p[0].biospecimens[1].external_sample_id,
                         'Test_Sample_1')
        self.assertEqual(Biospecimen.query.count(), 2)

    def test_one_to_many_relationship_delete(self):
        """
        Test Deleting one of the biospecimens
        """
        # create a participant with a biospecimen
        (participant_id,
        sample_id,
        aliquot_id) = self.create_participant_biospecimen()
        p = Participant.query.filter_by(
            external_id=participant_id).one_or_none()

        # adding another biospecimen to participant
        data = self._make_biospecimen(external_sample_id='Test_Sample_1',
                                      external_aliquot_id='Test_Aliquot_1')
        ids = self.create_seqexp()
        s = Biospecimen(**data, participant_id=p.kf_id,
                        sequencing_center_id=ids['sequencing_center_id'])
        db.session.add(s)
        db.session.commit()

        # Delete Biospecimen
        db.session.delete(s)
        db.session.commit()
        self.assertEqual(Biospecimen.query.count(), 1)

    def _make_biospecimen(self, external_sample_id=None,
                          external_aliquot_id=None):
        '''
        Convenience method to create a biospecimen with a given source name
        '''
        dt = datetime.now()
        body = {
            'external_sample_id': external_sample_id,
            'external_aliquot_id': external_aliquot_id,
            'source_text_tissue_type': 'Normal',
            'composition': 'Test_comp_0',
            'source_text_anatomical_site': 'Brain',
            'age_at_event_days': 456,
            'source_text_tumor_descriptor': 'Metastatic',
            'shipment_origin': 'CORIELL',
            'analyte_type': 'DNA',
            'concentration_mg_per_ml': 100.0,
            'volume_ml': 12.67,
            'shipment_date': dt,
            'uberon_id_anatomical_site': 'UBERON:0000955',
            'spatial_descriptor': 'left side',
            'ncit_id_tissue_type': 'Test',
            'ncit_id_anatomical_site': 'C12439'
        }
        return body

    def create_seqexp(self):
        """
        create sequencing_center and
        sequencing experiment save the above entities to db
        returns sequencing_experiment_id
        """
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
        se = SequencingExperiment(external_id="Test_seq_ex_o",
                                  experiment_strategy="WGS",
                                  is_paired_end="True",
                                  platform="Test_platform",
                                  sequencing_center_id=sc.kf_id)
        sc.sequencing_experiments.extend([se])
        db.session.add(sc)
        db.session.commit()
        ids = {
                'sequencing_experiment_id': se.kf_id,
                'sequencing_center_id':sc.kf_id
                }
        return ids
