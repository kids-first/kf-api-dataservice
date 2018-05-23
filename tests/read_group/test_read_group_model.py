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
from dataservice.api.read_group.models import ReadGroup
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from tests.utils import IndexdTestCase
from tests.mocks import MockIndexd, MockResp


class ModelTest(IndexdTestCase):
    """
    Test database model
    """
    def create_read_group(self):
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

    def test_create_and_find_read_group(self):
        """
        Test creation of read_group 
        """
        self._create_entities()
        gf = GenomicFile.query.first()
        rg = ReadGroup(genomic_file_id=gf.kf_id)
        db.session.add(rg)
        db.session.commit()

        self.assertEqual(GenomicFile.query.count(), 1)
        self.assertEqual(ReadGroup.query.count(), 1)
        self.assertEqual(ReadGroup.query.first().genomic_file, gf)

    def test_no_gf(self):
        """
        Test creation of read_group without a genomic_file
        """
        rg = ReadGroup()
        self.assertRaises(IntegrityError, db.session.add(rg))

    def test_update_read_group(self):
        """
        Test Updating read_group 
        """
        self._create_entities()
        gf = GenomicFile.query.first()
        rg = ReadGroup(genomic_file_id=gf.kf_id)
        db.session.add(rg)
        db.session.commit()

        self.assertEqual(ReadGroup.query.count(), 1)
        rg = ReadGroup.query.first()
        rg.paired_end = 1
        rg.flow_cell = 8
        db.session.add(rg)
        db.session.commit()

        rg = ReadGroup.query.first()
        self.assertEqual(rg.paired_end, 1)
        self.assertEqual(rg.flow_cell, '8')

    def test_delete_read_group(self):
        """
        Test Deleting sequencing_experiment
        """
        self._create_entities()
        gf = GenomicFile.query.first()
        rg = ReadGroup(genomic_file_id=gf.kf_id)
        db.session.add(rg)
        db.session.commit()

        self.assertEqual(ReadGroup.query.count(), 1)

        db.session.delete(rg)
        db.session.commit()

        self.assertEqual(ReadGroup.query.count(), 0)

    def test_delete_orphans(self):
        """
        Test that deleting a genomic_file will delete its read_group
        """
        self._create_entities()
        gf = GenomicFile.query.first()
        rg = ReadGroup(genomic_file_id=gf.kf_id)
        db.session.add(rg)
        db.session.commit()

        self.assertEqual(ReadGroup.query.count(), 1)
        self.assertEqual(GenomicFile.query.count(), 1)
        
        db.session.delete(gf)
        db.session.commit()

        self.assertEqual(ReadGroup.query.count(), 0)
        self.assertEqual(GenomicFile.query.count(), 0)

    def _create_entities(self):
        """
        Make all entities up to genomic_file
        """
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
        dt = datetime.utcnow()
        seq_experiment_data = {
            'external_id': 'experiment 1',
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
        se1 = SequencingExperiment(**seq_experiment_data,
                                   sequencing_center_id=sc.kf_id)

        # Create biospecimen
        bs = Biospecimen(external_sample_id='bio1', analyte_type='dna',
                         participant_id=p.kf_id,
                         sequencing_center_id=sc.kf_id)
        # Create genomic file
        kwargs = {
            'file_name': 'reads.fq',
            'data_type': 'Unaligned Reads',
            'file_format': '.fq',
            'urls': ['s3://seq-data/reads.fq'],
            'hashes': {'md5': str(uuid.uuid4())},
            'controlled_access': True,
            'is_harmonized': False,
            'reference_genome': None
        }
        gf = GenomicFile(**kwargs, biospecimen_id=bs.kf_id,
                         sequencing_experiment_id=se1.kf_id)
        bs.genomic_files = [gf]
        p.biospecimens = [bs]
        db.session.add(p)
        db.session.commit()
