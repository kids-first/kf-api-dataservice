from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.sample.models import Sample
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def create_participant_sample_aliquot_seqexp(self):
        """
        create a participant, sample, aliquot and sequencing experiment
        save the above entities to db
        returns participant_id, sample_id, aliquot_id and
        sequencing_experiment_id
        """
        # Create study
        study = Study(external_id='phs001')

        dt = datetime.now()
        participant_id = "Test_Subject_0"
        sample_id = "Test_Sample_0"
        aliquot_id = "Test_Aliquot_0"
        sequencing_experiment_id = "Test_SequencingExperiment_0"
        sample_data = {
            'external_id': sample_id,
            'tissue_type': 'Normal',
            'composition': 'Test_comp_0',
            'anatomical_site': 'Brain',
            'age_at_event_days': 456,
            'tumor_descriptor': 'Metastatic'
        }
        aliquot_data = {
            'external_id': aliquot_id,
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Broad Institute',
            'analyte_type': 'DNA',
            'concentration': 100,
            'volume': 12.67,
            'shipment_date': dt
        }
        seq_experiment_data = {
            'external_id': sequencing_experiment_id,
            'experiment_date': dt,
            'experiment_strategy': 'WGS',
            'center': 'Broad Institute',
            'library_name': 'Test_library_name_0',
            'library_strand': 'Unstranded',
            'is_paired_end': True,
            'platform': 'Test_platform_name_0',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        sequencing_experiment_0 = SequencingExperiment(
            **seq_experiment_data)
        aliquot_0 = Aliquot(
            **aliquot_data,
            sequencing_experiments=[sequencing_experiment_0])
        sample_0 = Sample(**sample_data, aliquots=[aliquot_0])
        participant_0 = Participant(
            external_id=participant_id,
            samples=[sample_0],
            study=study)
        db.session.add(participant_0)
        db.session.commit()
        ids = {'participant_id': participant_id,
               'sample_id': sample_id,
               'aliquot_id': aliquot_id,
               'sequencing_experiment_id': sequencing_experiment_id}
        return ids

    def test_create_seqexp_aliquot_sample_participant(self):
        """
        Test creation of aliquot via sample and person
        """
        ids = self.create_participant_sample_aliquot_seqexp()
        s = Sample.query.filter_by(external_id=ids['sample_id']).one_or_none()
        p = Participant.query.filter_by(
            external_id=ids['participant_id']).one_or_none()
        a = Aliquot.query.filter_by(
            external_id=ids['aliquot_id']).one_or_none()
        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertEqual(p.kf_id, s.participant_id)
        self.assertEqual(p.samples[0].external_id, s.external_id)
        self.assertEqual(p.samples[0].aliquots[0].external_id, a.external_id)
        self.assertEqual(p.samples[0].aliquots[0].sequencing_experiments[0].
                         external_id, e.external_id)

    def test_create_sequencing_experiment(self):
        """
        Test creation of sequencing_exeriment
        """
        # Create study
        study = Study(external_id='phs001')

        dt = datetime.now()
        participant_id = "Test_Subject_0"
        # creating participant
        p = Participant(external_id=participant_id, study=study)
        db.session.add(p)
        db.session.commit()

        # Creating Sample
        s = Sample(
            external_id='Test_Sample_0',
            tissue_type='Normal',
            composition='Test_comp_0',
            anatomical_site='Brain',
            age_at_event_days=456,
            participant_id=p.kf_id)
        db.session.add(s)
        db.session.commit()

        # creating aliquot
        aliquot_data = {
            'external_id': 'Test_Aliquot_0',
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Broad Institute',
            'analyte_type': 'DNA',
            'concentration': 100,
            'volume': 12.67,
            'shipment_date': dt
        }
        a = Aliquot(**aliquot_data, sample_id=s.kf_id)
        db.session.add(a)
        db.session.commit()

        # creating sequencing experiment
        seq_experiment_data = {
            'external_id': 'Test_SequencingExperiment_0',
            'experiment_date': dt,
            'experiment_strategy': 'WGS',
            'center': 'Broad Institute',
            'library_name': 'Test_library_name_0',
            'library_strand': 'Unstranded',
            'is_paired_end': True,
            'platform': 'Test_platform_name_0',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        e = SequencingExperiment(
            **seq_experiment_data, aliquot_id=a.kf_id)
        db.session.add(e)
        db.session.commit()

        self.assertEqual(SequencingExperiment.query.count(), 1)
        new_seq_exp = SequencingExperiment.query.first()
        self.assertGreater(new_seq_exp.created_at, dt)
        self.assertGreater(new_seq_exp.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_seq_exp.uuid)), uuid.UUID)
        self.assertEqual(
            new_seq_exp.external_id,
            "Test_SequencingExperiment_0")
        self.assertEqual(new_seq_exp.experiment_strategy, "WGS")
        self.assertEqual(new_seq_exp.center, "Broad Institute")
        self.assertEqual(new_seq_exp.library_name, 'Test_library_name_0')
        self.assertGreaterEqual(new_seq_exp.experiment_date, dt)
        self.assertEqual(new_seq_exp.instrument_model, '454 GS FLX Titanium')
        self.assertEqual(new_seq_exp.mean_depth, 40)
        self.assertEqual(new_seq_exp.aliquot_id, a.kf_id)

    def test_find_sequencing_experiment(self):
        """
        test finding the sequencing_experiment with sequencing_experiment_id
        """
        dt = datetime.now()
        ids = self.create_participant_sample_aliquot_seqexp()

        # get sequencing_experiment
        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertEqual(e.external_id, "Test_SequencingExperiment_0")
        self.assertEqual(e.experiment_strategy, "WGS")
        self.assertEqual(e.center, "Broad Institute")
        self.assertEqual(e.library_name, 'Test_library_name_0')
        self.assertGreaterEqual(e.experiment_date, dt)
        self.assertEqual(e.instrument_model, '454 GS FLX Titanium')
        self.assertEqual(e.mean_depth, 40)
        self.assertEqual(e.external_id, ids['sequencing_experiment_id'])

    def test_update_sequencing_experiment(self):
        """
        Test Updating sequencing_experiment
        """
        dt = datetime.now()
        ids = self.create_participant_sample_aliquot_seqexp()

        # get sequencing_experiment
        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()

        e.experiment_strategy = "WXS"
        db.session.commit()

        # get updated sequencing_experiment
        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertEqual(e.experiment_strategy, "WXS")
        self.assertEqual(e.external_id, ids['sequencing_experiment_id'])

    def test_delete_sequencing_experiment(self):
        """
        Test Deleting sequencing_experiment
        """
        ids = self.create_participant_sample_aliquot_seqexp()

        # get sequencing_experiment
        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()

        # Delete sequencing_experiment
        db.session.delete(e)
        db.session.commit()

        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertIs(e, None)
        self.assertIsNone(
            Aliquot.query.filter_by(
                external_id=ids['sequencing_experiment_id']).one_or_none())
        self.assertEqual(Aliquot.query.count(), 1)
        self.assertEqual(Sample.query.count(), 1)
        self.assertEqual(Participant.query.count(), 1)

    def test_delete_seqexp_aliquot_sample_participant(self):
        """
        Test deleting sequencing_experiment via aliquot, sample and participant
        """

        ids = self.create_participant_sample_aliquot_seqexp()

        # Delete Participant
        p = Participant.query.first()
        db.session.delete(p)
        db.session.commit()

        s = Sample.query.filter_by(external_id=ids['sample_id']).one_or_none()
        self.assertIs(s, None)
        # Check no sample exists in participant
        self.assertIsNone(
            Participant.query.filter_by(
                external_id=ids['sample_id']).one_or_none())

        a = Aliquot.query.filter_by(
            external_id=ids['aliquot_id']).one_or_none()
        self.assertIs(a, None)

        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertIs(e, None)

        # Check No Sequencialexperiment exists in aliquot
        self.assertIsNone(
            Aliquot.query.filter_by(
                external_id=ids['sequencing_experiment_id']).one_or_none())

    def test_not_null_constraint(self):
        """
        Test sequencing_experiment cannot be created with out aliquot,
        sample or participant
        """
        dt = datetime.now()
        # Create sequencialexperiment without aliquot kf_id
        seq_experiment_data = {
            'external_id': 'Test_SequencingExperiment_0',
            'experiment_date': dt,
            'experiment_strategy': 'WGS',
            'center': 'Broad Institute',
            'library_name': 'Test_library_name_0',
            'library_strand': 'Unstranded',
            'is_paired_end': True,
            'platform': 'Test_platform_name_0',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        e = SequencingExperiment(**seq_experiment_data)

        # Add sequencing_experiment to db
        self.assertRaises(IntegrityError, db.session.add(e))

    def test_foreign_key_constraint(self):
        """
        Test sequencing_experiment cannot be created with out aliquot,
        sample or participant
        """
        dt = datetime.now()
        # Create sequencialexperiment
        seq_experiment_data = {
            'external_id': 'Test_SequencingExperiment_0',
            'experiment_date': dt,
            'experiment_strategy': 'WGS',
            'center': 'Broad Institute',
            'library_name': 'Test_library_name_0',
            'library_strand': 'Unstranded',
            'is_paired_end': True,
            'platform': 'Test_platform_name_0',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        e = SequencingExperiment(**seq_experiment_data, aliquot_id='')

        # Add aliquot to db
        self.assertRaises(IntegrityError, db.session.add(e))

    def test_one_to_many_seqexp_create(self):
        """
        Test creating multiple sequencial experiments to the aliquot
        """
        dt = datetime.now()
        ids = self.create_participant_sample_aliquot_seqexp()

        # get aliquot
        a = Aliquot.query.filter_by(external_id=ids['aliquot_id']).all()

        # adding second sequencialexperiment to aliquot
        seq_experiment_data = {
            'external_id': 'Test_SequencingExperiment_1',
            'experiment_date': dt,
            'experiment_strategy': 'WXS',
            'center': 'Broad Institute',
            'library_name': 'Test_library_name_1',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'Test_platform_name_1',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        e = SequencingExperiment(
            **seq_experiment_data,
            aliquot_id=a[0].kf_id)

        db.session.add(e)
        db.session.commit()

        p = Participant.query.filter_by(
            external_id=ids['participant_id']).all()
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(p[0].samples[0].external_id, 'Test_Sample_0')

        s = Sample.query.filter_by(external_id=ids['sample_id']).all()
        self.assertEqual(Sample.query.count(), 1)
        self.assertEqual(s[0].aliquots[0].external_id, 'Test_Aliquot_0')

        a = Aliquot.query.filter_by(external_id=ids['aliquot_id']).all()
        self.assertEqual(Aliquot.query.count(), 1)

        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).all()
        self.assertEqual(SequencingExperiment.query.count(), 2)

    def test_one_to_many_seqexp_update(self):
        """
        Test updating one of sequencial experiments to the aliquot
        """
        dt = datetime.now()
        ids = self.create_participant_sample_aliquot_seqexp()

        # get aliquot
        a = Aliquot.query.filter_by(external_id=ids['aliquot_id']).all()

        # adding second sequencialexperiment to aliquot
        seq_experiment_data = {
            'external_id': 'Test_SequencingExperiment_1',
            'experiment_date': dt,
            'experiment_strategy': 'WXS',
            'center': 'Broad Institute',
            'library_name': 'Test_library_name_1',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'Test_platform_name_1',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        e = SequencingExperiment(
            **seq_experiment_data,
            aliquot_id=a[0].kf_id)

        db.session.add(e)
        db.session.commit()

        # Get sequencial experiments
        e1 = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        e2 = SequencingExperiment.query.filter_by(
            external_id=e.external_id).one_or_none()

        # update e1 and e2
        e1[0].is_paired_end = False
        e2[0].experiment_strategy = 'WGS'
        db.session.commit()

        e1 = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        e2 = SequencingExperiment.query.filter_by(
            external_id=e.external_id).one_or_none()
        self.assertEqual(SequencingExperiment.query.count(), 2)
        self.assertEqual(e1[0].is_paired_end, False)
        self.assertEqual(e2[0].experiment_strategy, 'WGS')

    def test_one_to_many_seqexp_update(self):
        """
        Test deleting one of sequencial experiments from the aliquot
        """
        dt = datetime.now()
        ids = self.create_participant_sample_aliquot_seqexp()

        # get aliquot
        a = Aliquot.query.filter_by(external_id=ids['aliquot_id']).all()

        # adding second sequencialexperiment to aliquot
        seq_experiment_data = {
            'external_id': 'Test_SequencingExperiment_1',
            'experiment_date': dt,
            'experiment_strategy': 'WXS',
            'center': 'Broad Institute',
            'library_name': 'Test_library_name_1',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'Test_platform_name_1',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        e = SequencingExperiment(
            **seq_experiment_data,
            aliquot_id=a[0].kf_id)
        db.session.add(e)
        db.session.commit()

        # Get sequencial experiments
        e1 = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        e2 = SequencingExperiment.query.filter_by(
            external_id=e.external_id).one_or_none()

        # delete e2
        db.session.delete(e2)
        db.session.commit()

        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(Sample.query.count(), 1)
        self.assertEqual(Aliquot.query.count(), 1)
        self.assertEqual(SequencingExperiment.query.count(), 1)
