from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def create_seqexp_seqcen(self):
        """
        create sequencial center save to db
        returns sequencing_center kf_id
        """
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(external_id='SC_0', name="Baylor")
            db.session.add(sc)
            db.session.commit()
        seq_data = {
            'external_id': 'Seq_0',
            'experiment_strategy': 'WXS',
            'library_name': 'Test_library_name_1',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'Test_platform_name_1'
        }
        seq_exp = SequencingExperiment(**seq_data,
                                       sequencing_center_id=sc.kf_id)
        db.session.add(seq_exp)
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
        self.assertEqual(SequencingExperiment.query.count(), 1)
        sc = SequencingCenter.query.one()

        self.assertEqual(sc.name, "Baylor")
        self.assertEqual(sc.kf_id, ids['sequencing_center_id'])
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
        Test deleting sequencing_center with existing sequencing_experiment
        """
        ids = self.create_seqexp_seqcen()

        # get sequencing_center
        e = SequencingCenter.query.one_or_none()
        db.session.delete(e)
        # Delete sequencing_center
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_not_null_constraint(self):
        """
        Test sequencing_center can be created with out name
        """
        # Create sequencing_center without name
        sc = SequencingCenter(external_id='SC_0')

        # Add sequencing_center to db
        db.session.add(sc)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_unique_constraint(self):
        """
        Test name field sequencing_center can not take duplicate name
        """
        ids = self.create_seqexp_seqcen()
        # Create sequencing_center with same value in name
        sc = SequencingCenter(external_id='SC_0', name='Baylor')

        # Add sequencing_center to db
        db.session.add(sc)
        with self.assertRaises(IntegrityError):
            db.session.commit()
