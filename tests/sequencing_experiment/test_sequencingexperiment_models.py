from datetime import datetime
import uuid

from sqlalchemy.exc import IntegrityError
from unittest.mock import patch

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from tests.utils import IndexdTestCase


MAX_SIZE_MB = 5000
MIN_SIZE_MB = 1000
MB_TO_BYTES = 1000000000


class ModelTest(IndexdTestCase):
    """
    Test database model
    """

    def create_seqexp(self):
        """
        create sequencing_center and
        sequencing experiment save the above entities to db
        returns sequencing_experiment_id
        """
        sc = SequencingCenter(name="Baylor")
        se_id = "Test_SequencingExperiment_0"
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        se = SequencingExperiment(
            **seq_experiment_data, sequencing_center_id=sc.kf_id)
        sc.sequencing_experiments.extend([se])
        db.session.add(sc)
        db.session.commit()
        ids = {'sequencing_experiment_id': se_id}
        return ids

    def test_create_and_find_sequencing_experiment(self):
        """
        Test creation of sequencing_exeriment
        """
        dt = datetime.now()
        # Create sequencing center
        sc = SequencingCenter(name="Baylor")
        # Create sequencing experiment
        se_id = 'Test_SequencingExperiment_0'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        e = SequencingExperiment(
            **seq_experiment_data, sequencing_center_id=sc.kf_id)
        sc.sequencing_experiments.extend([e])
        db.session.add(sc)
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
        ids = self.create_seqexp()

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
        self._create_entities()

        # Get seq exp, and track total gf count
        e = SequencingExperiment.query.first()
        kf_id = e.kf_id
        gf_count = GenomicFile.query.count()
        assert gf_count > 0

        # Delete sequencing_experiment
        db.session.delete(e)
        db.session.commit()

        # Check database
        # Exp deleted
        assert SequencingExperiment.query.get(kf_id) is None
        # All gfs still there, no cascade
        assert gf_count == GenomicFile.query.count()

    def test_not_null_constraint(self):
        """
        Test sequencing_experiment cannot be created with out sequencing_center
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
        Test sequencing_experiment cannot be created with out
        sequencing_center
        """
        # Create sequencialexperiment
        se_id = 'Test_SequencingExperiment_0'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)

        e = SequencingExperiment(**seq_experiment_data)
        # Check for database
        self.assertRaises(IntegrityError, db.session.add(e))

    def test_delete_orphans(self):
        """
        Test that orphaned seq exps are deleted
        Orphans are seq exp with 0 genomic_files
        """
        # Create entities
        self._create_entities()

        # Delete genomic files from seq exp 1
        se1 = SequencingExperiment.query.filter_by(external_id='se1').one()
        se2 = SequencingExperiment.query.filter_by(external_id='se2').one()
        for gf in se1.genomic_files:
            db.session.delete(gf)
        db.session.commit()

        # Check that orphan was deleted and other seq exp was unaffected
        self.assertEqual(1, SequencingExperiment.query.count())
        self.assertEqual(se2, SequencingExperiment.query.first())
        self.assertEqual(len(se2.genomic_files),
                         len(SequencingExperiment.query.first().genomic_files))

        # Check that the seq exp still exists when it has at least one gf
        db.session.delete(se2.genomic_files[0])
        db.session.commit()
        self.assertEqual(1, SequencingExperiment.query.count())
        self.assertEqual(se2, SequencingExperiment.query.first())

    def _create_entities(self):
        # Create study
        study = Study(external_id='phs001')

        # Create participant
        p = Participant(external_id='p1',
                        is_proband=True, study=study)

        # Create sequencing_center
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()

        # Create sequencing experiments
        se1 = SequencingExperiment(**self._make_seq_exp('se1'),
                                   sequencing_center_id=sc.kf_id)
        se2 = SequencingExperiment(**self._make_seq_exp('se2'),
                                   sequencing_center_id=sc.kf_id)

        # Create biospecimen
        bs = Biospecimen(external_sample_id='bio1', analyte_type='dna',
                         participant_id=p.kf_id,
                         sequencing_center_id=sc.kf_id)
        # Create genomic files
        gfs = []
        for i in range(4):
            kwargs = {
                'file_name': 'file_{}'.format(i),
                'data_type': 'submitted aligned read',
                'file_format': '.cram',
                'urls': ['s3://file_{}'.format(i)],
                'hashes': {'md5': str(uuid.uuid4())},
                'controlled_access': True,
                'is_harmonized': True,
                'reference_genome': 'Test01'
            }
            gf = GenomicFile(**kwargs,
                             sequencing_experiment_id=se1.kf_id)
            if i % 2:
                se1.genomic_files.append(gf)
            else:
                se2.genomic_files.append(gf)
            gfs.append(gf)
        bs.genomic_files = gfs
        p.biospecimens = [bs]
        db.session.add(p)
        db.session.commit()

    def _make_seq_exp(self, external_id=None):
        '''
        Convenience method to create a sequencing experiment
        with a given source name
        '''
        dt = datetime.now()
        seq_experiment_data = {
            'external_id': external_id,
            'experiment_date': dt,
            'experiment_strategy': 'WXS',
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
