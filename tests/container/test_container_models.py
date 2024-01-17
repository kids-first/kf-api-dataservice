from dataservice.extensions import db
from dataservice.api.container.models import Container
from tests.utils import FlaskTestCase

from tests.create import make_container


class ContainerModelTest(FlaskTestCase):
    """
    Test container database model
    """

    def test_create_container(self):
        """
        Test creation of a container
        """
        c = make_container(specimen_status="available")
        container = Container.query.filter_by(
            external_aliquot_id=c.external_aliquot_id,
        ).one()

        assert container.external_aliquot_id == "container-01"
        assert container.biospecimen.external_sample_id == "bs1"

    def test_delete_container(self):
        """
        Test that a container is removed
        """
        c = make_container()
        container = Container.query.filter_by(
            external_aliquot_id=c.external_aliquot_id,
        ).one()
        db.session.delete(container)
        db.session.commit()

        assert Container.query.count() == 0

    def test_update_container(self):
        """
        Test that container properties may be updated
        """
        c = make_container()
        assert c.external_aliquot_id == 'container-01'

        c.external_aliquot_id = 'container-02'
        db.session.add(c)
        db.session.commit()

        assert Container.query.get(
            c.kf_id).external_aliquot_id == 'container-02'
