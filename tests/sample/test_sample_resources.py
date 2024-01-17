import json

from flask import url_for

from dataservice.api.sample.models import Sample

from tests.utils import FlaskTestCase
from tests.create import make_sample, make_participant

SAMPLES_URL = 'api.samples'
SAMPLES_LIST_URL = 'api.samples_list'


class SampleTest(FlaskTestCase):
    """
    Test sample api endpoints
    """

    def test_post_sample(self):
        """
        Test creating a new sample
        """
        p = make_participant()
        data = {
            "external_id": "sample-01",
            "participant_id": p.kf_id
        }
        # Send post request
        response = self.client.post(url_for(SAMPLES_LIST_URL),
                                    data=json.dumps(data),
                                    headers=self._api_headers())

        assert response.status_code == 201

        resp = json.loads(response.data.decode('utf-8'))
        assert "sample" in resp['_status']['message']
        assert "created" in resp['_status']['message']

        resp = resp['results']
        sample = Sample.query.get(resp['kf_id'])
        assert sample.external_id == resp['external_id']

    def test_get_sample(self):
        """
        Test retrieving a sample by id
        """
        s = make_sample(external_id='TESTXXX')

        response = self.client.get(
            url_for(SAMPLES_URL, kf_id=s.kf_id),
            headers=self._api_headers()
        )
        resp = json.loads(response.data.decode('utf-8'))
        assert response.status_code == 200

        resp = resp['results']
        sample = Sample.query.get(resp["kf_id"])
        assert sample
        assert sample.external_id == resp["external_id"]

    def test_get_all_samples(self):
        """
        Test retrieving all samples
        """
        make_sample(external_id='TEST')

        response = self.client.get(
            url_for(SAMPLES_LIST_URL),
            headers=self._api_headers()
        )
        assert response.status_code == 200
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')

        assert isinstance(content, list)
        assert len(content) == 1

    def test_patch_sample(self):
        """
        Test updating an existing sample
        """
        orig = Sample.query.count()
        s = make_sample(external_id='TEST')
        body = {
            'external_id': 'NEWID',
        }
        assert (orig + 1) == Sample.query.count()

        response = self.client.patch(url_for(SAMPLES_URL,
                                             kf_id=s.kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        assert response.status_code == 200

        # Message
        resp = json.loads(response.data.decode('utf-8'))
        assert "sample" in resp['_status']['message']
        assert "updated" in resp['_status']['message']

        # Content - check only patched fields are updated
        sample = Sample.query.get(s.kf_id)
        assert sample.external_id == resp['results']['external_id']

    def test_delete_sample(self):
        """
        Test deleting a sample by id
        """
        orig = Sample.query.count()
        s = make_sample(external_id='TEST')
        kf_id = s.kf_id

        response = self.client.delete(url_for(SAMPLES_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        assert response.status_code == 200
        assert orig == Sample.query.count()

        response = self.client.get(url_for(SAMPLES_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        assert response.status_code == 404
