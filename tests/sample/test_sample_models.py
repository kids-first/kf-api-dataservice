from dataservice.extensions import db
from dataservice.api.sample.models import Sample
from dataservice.api.container.models import Container
from tests.utils import FlaskTestCase

from tests.create import make_sample, make_container


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
        Test that a sample and its containers are removed
        """
        s = make_sample()
        make_container(
            external_id="c1", sample=s, force_create=True
        )
        sample = Sample.query.filter_by(external_id=s.external_id).one()
        db.session.delete(sample)
        db.session.commit()

        assert Sample.query.count() == 0
        assert Container.query.count() == 0

    def test_delete_container_orphan(self):
        """
        Test that a sample is deleted when all related containers
        are deleted
        """
        # Make two samples with containers
        s1 = make_sample(external_id="s01", force_create=True)
        s2 = make_sample(external_id="s02", force_create=True)
        make_container(
            external_id="c1", sample=s1, force_create=True
        )
        make_container(
            external_id="c2", sample=s2, force_create=True
        )
        assert len(s1.containers) == 1

        # Make orphan sample
        result = Sample.query.filter_by(external_id="s01").one()
        for ct in result.containers:
            db.session.delete(ct)
        db.session.commit()

        # Check that orphan sample is deleted
        result = Sample.query.filter_by(external_id="s01").one_or_none()
        assert result is None

        # Check that other sample still exists
        result = Sample.query.filter_by(external_id="s02").one_or_none()
        assert result
        assert len(result.containers) == 1

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
