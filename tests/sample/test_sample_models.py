from dataservice.extensions import db
from dataservice.api.sample.models import Sample
from dataservice.api.biospecimen.models import Biospecimen
from tests.utils import FlaskTestCase

from tests.create import make_sample, make_biospecimen


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
        Test that a sample and its biospecimen's sample_id is set to null 
        """
        s = make_sample()
        b = make_biospecimen(
            external_sample_id="c1", sample=s, force_create=True
        )
        bs_kf_id = b.kf_id
        sample = Sample.query.filter_by(external_id=s.external_id).one()
        db.session.delete(sample)
        db.session.commit()

        assert Sample.query.count() == 0
        assert Biospecimen.query.count() == 1

        assert Biospecimen.query.get(bs_kf_id).sample_id is None

    def test_no_delete_sample_orphan(self):
        """
        Test that a sample is NOT deleted when all related biospecimens
        are deleted
        """
        # Make two samples with biospecimens
        s1 = make_sample(external_id="s01", force_create=True)
        s2 = make_sample(external_id="s02", force_create=True)
        make_biospecimen(
            external_aliquot_id="c1", sample=s1, force_create=True
        )
        make_biospecimen(
            external_aliquot_id="c2", sample=s2, force_create=True
        )
        assert len(s1.biospecimens) == 1

        # Make orphan sample
        result = Sample.query.filter_by(external_id="s01").one()
        for ct in result.biospecimens:
            db.session.delete(ct)
        db.session.commit()

        # Check that orphan sample is not deleted
        result = Sample.query.filter_by(external_id="s01").one_or_none()
        assert result.kf_id

        # Check that other sample still exists
        result = Sample.query.filter_by(external_id="s02").one_or_none()
        assert result.kf_id
        assert len(result.biospecimens) == 1

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
