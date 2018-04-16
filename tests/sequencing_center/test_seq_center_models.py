from datetime import datetime
import uuid
import random

from dataservice.extensions import db
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError

MAX_SIZE_MB = 5000
MIN_SIZE_MB = 1000
MB_TO_BYTES = 1000000000


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def create_seqexp_seqcen(self):
        """
        create a sequencing experiment and sequencial center save to db
        returns sequencing_center kf_id
        """
        se_id = "Test_SequencingExperiment_0"
        seq_experiment_data = self._make_seq_exp(external_id=se_id)
        se = SequencingExperiment(
            **seq_experiment_data)
        db.session.add(se)
        db.session.commit()
        sc = SequencingCenter(name="Baylor", sequencing_experiment_id=se.kf_id)
        db.session.add(sc)
        db.session.commit()
        ids = {'sequencing_center_id': sc.kf_id}
        return ids

    def test_create_and_find_sequencing_center(self):
        """
        Test creation of sequencing_center
        """
        dt = datetime.now()
        ids = self.create_seqexp_seqcen()

        self.assertEqual(SequencingCenter.query.count(), 1)
        sc = SequencingCenter.query.one()

        self.assertEqual(sc.name, "Baylor")
        self.assertGreater(sc.created_at, dt)
        self.assertGreater(sc.modified_at, dt)
        self.assertIs(type(uuid.UUID(sc.uuid)), uuid.UUID)

    def test_update_sequencing_center(self):
        """
        Test Updating sequencing_center
        """
        ids = self.create_seqexp_seqcen()
        # get sequencing_center
        sc = SequencingCenter.query.one_or_none()

        sc.name = "Baylor"
        db.session.commit()

        # get updated sequencing_center
        e = SequencingCenter.query.one_or_none()
        self.assertEqual(e.name, "Baylor")

    def test_delete_sequencing_center(self):
        """
        Test Deleting sequencing_center
        """
        ids = self.create_seqexp_seqcen()

        # get sequencing_center
        e = SequencingCenter.query.one_or_none()

        # Delete sequencing_center
        db.session.delete(e)
        db.session.commit()

        e = SequencingCenter.query.one_or_none()
        self.assertIs(e, None)

    def test_not_null_constraint(self):
        """
        Test sequencing_center cannot be created with out sequencing experiment
        """
        # Create sequencing_center without sequencing experiment kf_id
        sc = SequencingCenter(name='Baylor',sequencing_experiment_id='')

        # Add sequencing_center to db
        self.assertRaises(IntegrityError, db.session.add(sc))

    def test_foreign_key_constraint(self):
        """
        Test sequencing_center cannot be created with out
        sequencing center
        """
        # Create sequencing_center without sequencing experiment kf_id
        sc = SequencingCenter(name='Baylor')

        # Add sequencing_center to db
        self.assertRaises(IntegrityError, db.session.add(sc))

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
