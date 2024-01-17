from dataservice.extensions import db
from dataservice.api.sample.models import Sample
from tests.utils import FlaskTestCase

from tests.create import make_sample


class SampleModelTest(FlaskTestCase):
    """
    Test sample database model
    """

    def test_create_sample(self):
        """
        Test creation of a sample
        """
        s = make_sample()
        sample = Sample.query.filter_by(external_id=s.external_id).one()

        assert sample.participant.external_id == "p1"

    def test_delete_sample(self):
        """
        Test that a sample is removed
        """
        s = make_sample()
        sample = Sample.query.filter_by(external_id=s.external_id).one()
        db.session.delete(sample)
        db.session.commit()

        assert Sample.query.count() == 0

    def test_delete_container_orphan(self):
        """
        Test that a sample is deleted when all related containers
        are deleted
        """
        # Make two samples with containers

        # Make orphan sample

        # Check that orphan sample is deleted

        # Check that other sample still exists

    def test_update_sample(self):
        """
        Test that sample properties may be updated
        """
        s = make_sample()
        assert s.external_id == 'sample-01'

        s.external_id = 'sample-02'
        db.session.add(s)
        db.session.commit()

        assert Sample.query.get(s.kf_id).external_id == 'sample-02'
