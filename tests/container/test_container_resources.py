import json

from flask import url_for

from dataservice.api.container.models import Container

from tests.utils import FlaskTestCase
from tests import create

CONTAINERS_URL = 'api.containers'
CONTAINERS_LIST_URL = 'api.containers_list'


class ContainerTest(FlaskTestCase):
    """
    Test container api endpoints
    """

    def test_post_container(self):
        """
        Test creating a new container
        """
        bs = create.make_biospecimen()
        sp = create.make_sample()
        data = {
            "external_id": "container-01",
            "specimen_status": "available",
            "biospecimen_id": bs.kf_id,
            "sample_id": sp.kf_id,
        }
        # Send post request
        response = self.client.post(url_for(CONTAINERS_LIST_URL),
                                    data=json.dumps(data),
                                    headers=self._api_headers())

        assert response.status_code == 201

        resp = json.loads(response.data.decode('utf-8'))
        assert "container" in resp['_status']['message']
        assert "created" in resp['_status']['message']
        assert "biospecimen" in resp["_links"]
        assert "sample" in resp["_links"]

        resp = resp["results"]
        container = Container.query.get(resp['kf_id'])
        assert container.external_id == resp['external_id']

    def test_get_container(self):
        """
        Test retrieving a container by id
        """
        s = create.make_container(external_id='foobar')

        response = self.client.get(
            url_for(CONTAINERS_URL, kf_id=s.kf_id),
            headers=self._api_headers()
        )
        resp = json.loads(response.data.decode('utf-8'))
        assert response.status_code == 200

        resp = resp['results']
        container = Container.query.get(resp["kf_id"])
        assert container
        assert container.external_id == resp["external_id"]

    def test_get_all_containers(self):
        """
        Test retrieving all containers
        """
        create.make_container(external_id='TEST')

        response = self.client.get(
            url_for(CONTAINERS_LIST_URL),
            headers=self._api_headers()
        )
        assert response.status_code == 200
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')

        assert isinstance(content, list)
        assert len(content) == 1

    def test_patch_container(self):
        """
        Test updating an existing container
        """
        orig = Container.query.count()
        s = create.make_container(external_id='TEST')
        body = {
            'external_id': 'NEWID',
        }
        assert (orig + 1) == Container.query.count()

        response = self.client.patch(url_for(CONTAINERS_URL,
                                             kf_id=s.kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        assert response.status_code == 200

        # Message
        resp = json.loads(response.data.decode('utf-8'))
        assert "container" in resp['_status']['message']
        assert "updated" in resp['_status']['message']

        # Content - check only patched fields are updated
        container = Container.query.get(s.kf_id)
        assert (
            container.external_id ==
            resp['results']['external_id']
        )

    def test_delete_container(self):
        """
        Test deleting a container by id
        """
        orig = Container.query.count()
        s = create.make_container(external_id='TEST')
        kf_id = s.kf_id

        response = self.client.delete(url_for(CONTAINERS_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        assert response.status_code == 200
        assert orig == Container.query.count()

        response = self.client.get(url_for(CONTAINERS_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        json.loads(response.data.decode('utf-8'))
        assert response.status_code == 404
