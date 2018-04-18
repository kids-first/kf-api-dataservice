from datetime import datetime
import uuid
import random

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_center.models import SequencingCenter
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
        ids = self.create_seqexp()

        # get sequencing_experiment
        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()

        # Delete sequencing_experiment
        db.session.delete(e)
        db.session.commit()

        e = SequencingExperiment.query.filter_by(
            external_id=ids['sequencing_experiment_id']).one_or_none()
        self.assertIs(e, None)

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
        dt = datetime.now()
        # Create sequencialexperiment
        se_id = 'Test_SequencingExperiment_0'
        seq_experiment_data = self._make_seq_exp(external_id=se_id)

        e = SequencingExperiment(**seq_experiment_data)
        # Check for database
        self.assertRaises(IntegrityError, db.session.add(e))

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
