from datetime import datetime
import uuid
import random

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError

MAX_SIZE_MB = 5000
MIN_SIZE_MB = 1000
MB_TO_BYTES = 1000000000


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def create_participant_biospecimen_gf_seqexp(self):
        """
        create a participant, biospecimen, genomic_file and
        sequencing experiment save the above entities to db
        returns participant_id, biospecimen_id, genomic_file_id and
        sequencing_experiment_id
        """
        # Create study
        study = Study(external_id='phs001')

        dt = datetime.now()
        participant_id = "Test_Subject_0"
        sample_id = "Test_Sample_0"
        aliquot_id = "Test_Aliquot_0"
        genomic_file_id = "Test_Genomic_File_0"
        se_id = "Test_SequencingExperiment_0"
        biospecimen_data = {
            'external_sample_id': sample_id,
            'external_aliquot_id': aliquot_id,
            'tissue_type': 'Normal',
            'composition': 'Test_comp_0',
            'anatomical_site': 'Brain',
            'age_at_event_days': 456,
            'tumor_descriptor': 'Metastatic',
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Broad Institute',
            'analyte_type': 'DNA',
            'concentration': 100,
            'volume': 12.67,
            'shipment_date': dt
        }
        gf_data = {
            'file_name': 'file_0',
            'file_size': (random.randint(MIN_SIZE_MB, MAX_SIZE_MB) *
                      MB_TO_BYTES),
            'data_type': 'submitted aligned read',
            'file_format': '.cram',
            'file_url': 's3://file_0',
            'controlled_access': True,
            'md5sum': str(uuid.uuid4())
        }
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        sequencing_experiment_0 = SequencingExperiment(
            **seq_experiment_data)
        gf_0 = GenomicFile(
            **gf_data,
            sequencing_experiments=[sequencing_experiment_0])
        biospecimen_0 = Biospecimen(**biospecimen_data, genomic_files=[gf_0])
        participant_0 = Participant(
            external_id=participant_id,
            is_proband=True,
            biospecimens=[biospecimen_0],
            study=study)
        db.session.add(participant_0)
        db.session.commit()
        ids = {'participant_id': participant_id,
               'biospecimen_id': sample_id,
               'genomic_file_id': genomic_file_id,
               'sequencing_experiment_id': se_id}
        return ids

    def test_create_seqexp_gf_biospecimen_participant(self):
        """
        Test creation of experiment via biospecimen and person
        """
        ids = self.create_participant_biospecimen_gf_seqexp()
        s = Biospecimen.query.filter_by(
                                        external_sample_id=\
                                        ids['biospecimen_id']).one_or_none()
        p = Participant.query.filter_by(
            external_id=ids['participant_id']).one_or_none()
        g = GenomicFile.query.one_or_none()
        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertEqual(p.kf_id, s.participant_id)
        self.assertEqual(p.biospecimens[0].external_sample_id,
                         s.external_sample_id)
        self.assertEqual(p.biospecimens[0].genomic_files[0].file_name,
                         g.file_name)
        self.assertEqual(p.biospecimens[0].genomic_files[0]\
                         .sequencing_experiments[0].
                         external_id, e.external_id)

    def test_create_and_find_sequencing_experiment(self):
        """
        Test creation of sequencing_exeriment
        """
        # Create study
        study = Study(external_id='phs001')

        dt = datetime.now()
        participant_id = "Test_Subject_0"
        # creating participant
        p = Participant(external_id=participant_id, is_proband=True,
                        study=study)
        db.session.add(p)
        db.session.commit()

        # Creating Biospecimen
        s = Biospecimen(
            external_sample_id='Test_Sample0',
            tissue_type='Normal',
            composition='Test_comp_0',
            anatomical_site='Brain',
            age_at_event_days=456,
            analyte_type = 'dna',
            participant_id=p.kf_id)
        db.session.add(s)
        db.session.commit()
        gf_data = {
            'file_name': 'file_0',
            'file_size': (random.randint(MIN_SIZE_MB, MAX_SIZE_MB) *
                      MB_TO_BYTES),
            'data_type': 'submitted aligned read',
            'file_format': '.cram',
            'file_url': 's3://file_0',
            'controlled_access': True,
            'md5sum': str(uuid.uuid4())
        }
        g = GenomicFile(**gf_data, biospecimen_id=s.kf_id)
        db.session.add(g)
        db.session.commit()
        # creating sequencing experiment
        se_id = 'Test_SequencingExperiment_0'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        e = SequencingExperiment(
            **seq_experiment_data, genomic_file_id=g.kf_id)
        db.session.add(e)
        db.session.commit()

        self.assertEqual(SequencingExperiment.query.count(), 1)
        se = SequencingExperiment.query.one()
        for key, value in seq_experiment_data.items():
            self.assertEqual(value, getattr(se, key))
        self.assertGreater(se.created_at, dt)
        self.assertGreater(se.modified_at, dt)
        self.assertIs(type(uuid.UUID(se.uuid)), uuid.UUID)

    def test_update_sequencing_experiment(self):
        """
        Test Updating sequencing_experiment
        """
        dt = datetime.now()
        ids = self.create_participant_biospecimen_gf_seqexp()

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
        ids = self.create_participant_biospecimen_gf_seqexp()

        # get sequencing_experiment
        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()

        # Delete sequencing_experiment
        db.session.delete(e)
        db.session.commit()

        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertIs(e, None)
        self.assertEqual(GenomicFile.query.count(), 1)
        self.assertEqual(Biospecimen.query.count(), 1)
        self.assertEqual(Participant.query.count(), 1)

    def test_delete_seqexp_gf_biospecimen_participant(self):
        """
        Test deleting sequencing_experiment via genomic_file, biospecimen and
        participant
        """

        ids = self.create_participant_biospecimen_gf_seqexp()

        # Delete Participant
        p = Participant.query.first()
        db.session.delete(p)
        db.session.commit()

        s = Biospecimen.query.filter_by(external_sample_id=\
                                        ids['biospecimen_id']).one_or_none()
        self.assertIs(s, None)
        # Check no biospecimen exists in participant
        self.assertIsNone(
            Participant.query.filter_by(
                external_id=ids['biospecimen_id']).one_or_none())

        a = GenomicFile.query.one_or_none()
        self.assertIs(a, None)

        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertIs(e, None)

        # Check No Sequencialexperiment exists in genomic_file
        self.assertIsNone(
            GenomicFile.query.one_or_none())

    def test_not_null_constraint(self):
        """
        Test sequencing_experiment cannot be created with out genomic_file,
        biospecimen or participant
        """
        dt = datetime.now()
        # Create sequencialexperiment without genomic_file kf_id
        se_id = 'Test_SequencingExperiment_0'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        e = SequencingExperiment(**seq_experiment_data)

        # Add sequencing_experiment to db
        self.assertRaises(IntegrityError, db.session.add(e))

    def test_foreign_key_constraint(self):
        """
        Test sequencing_experiment cannot be created with out genomic_file,
        biospecimen or participant
        """
        dt = datetime.now()
        # Create sequencialexperiment
        se_id = 'Test_SequencingExperiment_0'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)

        e = SequencingExperiment(**seq_experiment_data, genomic_file_id='')

        # Add genomic_file to db
        self.assertRaises(IntegrityError, db.session.add(e))

    def test_one_to_many_seqexp_create(self):
        """
        Test creating multiple sequencial experiments to the genomic_file
        """
        dt = datetime.now()
        ids = self.create_participant_biospecimen_gf_seqexp()

        # get genomic_file
        a = GenomicFile.query.all()

        # adding second sequencialexperiment to genomic_file
        se_id = 'Test_SequencingExperiment_1'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        e = SequencingExperiment(
            **seq_experiment_data,
            genomic_file_id=a[0].kf_id)

        db.session.add(e)
        db.session.commit()

        p = Participant.query.filter_by(
            external_id=ids['participant_id']).all()
        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(p[0].biospecimens[0].external_sample_id,
                         'Test_Sample_0')

        s = Biospecimen.query.filter_by(external_sample_id=ids['biospecimen_id']
                                        ).all()
        self.assertEqual(Biospecimen.query.count(), 1)
        self.assertEqual(s[0].genomic_files[0].file_name, 'file_0')

        self.assertEqual(GenomicFile.query.count(), 1)

        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).all()
        self.assertEqual(SequencingExperiment.query.count(), 2)

    def test_one_to_many_seqexp_update(self):
        """
        Test updating one of sequencial experiments to the genomic_file
        """
        dt = datetime.now()
        ids = self.create_participant_biospecimen_gf_seqexp()

        # get genomic_file
        a = GenomicFile.query.all()

        # adding second sequencialexperiment to genomic_file
        se_id = 'Test_SequencingExperiment_1'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        e = SequencingExperiment(
            **seq_experiment_data,
            genomic_file_id=a[0].kf_id)

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
        Test deleting one of sequencial experiments from the genomic_file
        """
        dt = datetime.now()
        ids = self.create_participant_biospecimen_gf_seqexp()

        # get genomic_file
        a = GenomicFile.query.all()

        # adding second sequencialexperiment to genomic_file
        se_id = 'Test_SequencingExperiment_1'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        e = SequencingExperiment(
            **seq_experiment_data,
            genomic_file_id=a[0].kf_id)
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
        self.assertEqual(Biospecimen.query.count(), 1)
        self.assertEqual(GenomicFile.query.count(), 1)
        self.assertEqual(SequencingExperiment.query.count(), 1)

    def _make_seq_exp(self, external_id=None):
        '''
        Convenience method to create a sequencing experiment
        with a given source name
        '''
        dt = datetime.now()
        seq_experiment_data = {
            'external_id':external_id,
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
        return seq_experiment_data
