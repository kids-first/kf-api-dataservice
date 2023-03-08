from datetime import datetime

from dataservice.extensions import db
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_experiment.models import (
    SequencingExperiment,
    SequencingExperimentGenomicFile
)
from dataservice.api.sequencing_center.models import SequencingCenter
from tests.utils import IndexdTestCase


class ModelTest(IndexdTestCase):
    """
    Test database model
    """

    def test_create_and_find_sequencing_experiment(self):
        """
        Test creation of sequencing_experiment
        """
        ses, gfs = self._create_entities()
        self.assertEqual(SequencingExperiment.query.count(), 2)

        # Check that read group was linked to its gfs
        self.assertEqual(SequencingExperimentGenomicFile.query.filter_by(
            sequencing_experiment_id=ses[0].kf_id).count(), 2)

    def test_update_sequencing_experiment(self):
        """
        Test updating sequencing_experiment
        """
        self._create_entities()

        self.assertEqual(SequencingExperiment.query.count(), 2)
        se = SequencingExperiment.query.first()
        se.library = 'another library'
        se.platform = 'another platform'
        db.session.add(se)
        db.session.commit()

        se = SequencingExperiment.query.get(se.kf_id)
        self.assertEqual(se.library, 'another library')
        self.assertEqual(se.platform, 'another platform')

    def test_delete_sequencing_experiment(self):
        """
        Test deleting sequencing_experiment
        """
        ses, gfs = self._create_entities()

        self.assertEqual(GenomicFile.query.count(), 2)
        self.assertEqual(SequencingExperiment.query.count(), 2)
        self.assertEqual(SequencingExperimentGenomicFile.query.count(), 4)

        # Delete gf linked to 2 read groups
        db.session.delete(gfs[0])
        db.session.commit()
        self.assertEqual(GenomicFile.query.count(), 1)

        # Read groups should all still exist
        self.assertEqual(SequencingExperiment.query.count(), 2)

        # Only 2 link should remain in link table
        self.assertEqual(SequencingExperimentGenomicFile.query.count(), 2)
        self.assertEqual(
            SequencingExperimentGenomicFile.query.filter_by(
                genomic_file_id=gfs[0].kf_id).count(), 0)

    def test_delete_orphans(self):
        """
        Test that orphaned read groups are deleted
        Orphans are read groups with 0 genomic_files
        """
        ses, gfs = self._create_entities()

        self.assertEqual(SequencingExperiment.query.count(), 2)

        # Delete all gfs
        for gf in gfs:
            db.session.delete(gf)
        db.session.commit()

        # All read groups should be deleted since they're all orphans
        self.assertEqual(SequencingExperiment.query.count(), 0)

    def _create_entities(self):
        """
        Make all entities
        """
        # Create sequencing_center
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()

        # Data
        dt = datetime.now()
        kwargs = {
            'experiment_date': dt,
            'experiment_strategy': 'WXS',
            'library_name': 'library',
            'library_strand': 'Unstranded',
            'library_prep': 'totalRNAseq',
            'is_paired_end': False,
            'platform': 'ONT',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }

        # Create many to many se and gf
        ses = []
        gfs = []
        for i in range(2):
            gfs.append(
                GenomicFile(external_id='gf{}'.format(i))
            )
            ses.append(
                SequencingExperiment(**kwargs,
                                     external_id=f'se{i}',
                                     sequencing_center_id=sc.kf_id)
            )
        db.session.add(
            SequencingExperimentGenomicFile(genomic_file=gfs[0],
                                            sequencing_experiment=ses[0]))
        db.session.add(
            SequencingExperimentGenomicFile(genomic_file=gfs[0],
                                            sequencing_experiment=ses[1]))
        db.session.add(
            SequencingExperimentGenomicFile(genomic_file=gfs[1],
                                            sequencing_experiment=ses[0]))
        db.session.add(
            SequencingExperimentGenomicFile(genomic_file=gfs[1],
                                            sequencing_experiment=ses[1]))

        db.session.commit()

        return ses, gfs
