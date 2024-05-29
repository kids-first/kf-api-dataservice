import json
from flask import url_for

from dataservice.extensions import db
from dataservice.api.sample_relationship.models import SampleRelationship
from dataservice.api.sample.models import Sample
from tests.utils import FlaskTestCase
from tests.sample_relationship.common import create_relationships


SAMPLE_RELATIONSHIPS_URL = 'api.sample_relationships'
SAMPLE_RELATIONSHIPS_LIST_URL = 'api.sample_relationships_list'


class SampleRelationshipTest(FlaskTestCase):
    """
    Test sample_relationship api
    """

    def test_post(self):
        """
        Test create a new sample_relationship
        """
        _, rels = create_relationships()
        parent = rels[0].parent
        pid = parent.participant_id
        child = Sample(
            external_id="SA-003",
            sample_type="Saliva",
            participant_id=pid
        )
        db.session.add(child)
        db.session.commit()

        # Create new sample relationship
        kwargs = {
            "parent_id": parent.kf_id,
            "child_id": child.kf_id,
        }
        # Send get request
        response = self.client.post(url_for(SAMPLE_RELATIONSHIPS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        assert response.status_code == 201

        # Check response content
        response = json.loads(response.data.decode('utf-8'))

        sample_relationship = response['results']
        links = response['_links']
        parent_id = links["parent"].split("/")[-1]
        child_id = links["child"].split("/")[-1]

        sr = SampleRelationship.query.get(sample_relationship.get('kf_id'))

        assert sr.parent.kf_id == parent_id
        assert sr.child.kf_id == child_id
        assert SampleRelationship.query.count() == 5

    def test_no_multi_parent_samples(self):
        """
        Test that a child sample cannot have more than one parent sample
        """
        _, rels = create_relationships()

        child = rels[0].child
        pid = child.participant_id
        parent = Sample(
            external_id="SA-003",
            sample_type="Saliva",
            participant_id=pid
        )
        db.session.add(parent)
        db.session.commit()

        # Create new sample relationship
        kwargs = {
            "parent_id": parent.kf_id,
            "child_id": child.kf_id,
        }
        # Send get request
        response = self.client.post(url_for(SAMPLE_RELATIONSHIPS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        assert response.status_code == 400

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert "already exist" in response["_status"]["message"]

    def test_no_duplicate_relationships(self):
        """
        Test that if s1 -> s2 exists than it cannot be created again
        """
        _, rels = create_relationships()

        parent = rels[0].parent
        child = rels[0].child

        # Create new sample relationship
        kwargs = {
            "parent_id": parent.kf_id,
            "child_id": child.kf_id,
        }
        # Send get request
        response = self.client.post(url_for(SAMPLE_RELATIONSHIPS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        assert response.status_code == 400

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert "already exist" in response["_status"]["message"]

    def test_get(self):
        """
        Test retrieving a single sample_relationship
        """
        # Create and save sample_relationship to db
        _, rels = create_relationships()

        # Send get request
        kf_id = rels[0].kf_id
        response = self.client.get(url_for(SAMPLE_RELATIONSHIPS_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        # Check response status code
        assert response.status_code == 200

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sample_relationship = response['results']
        assert sample_relationship["kf_id"] == kf_id

    def test_get_all(self):
        """
        Test retrieving all sample_relationships
        """
        # Create and save sample_relationship to db
        _, rels = create_relationships()
        response = self.client.get(url_for(SAMPLE_RELATIONSHIPS_LIST_URL),
                                   headers=self._api_headers())
        # Check response status code
        assert response.status_code == 200

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        assert len(content) == 4

    def test_patch(self):
        """
        Test updating an existing sample_relationship
        """
        _, rels = create_relationships()
        sr = rels[0]
        kf_id = sr.kf_id

        # Update existing sample_relationship
        body = {
            'external_parent_id': 'foo'
        }
        response = self.client.patch(url_for(SAMPLE_RELATIONSHIPS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        assert response.status_code == 200

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        assert "sample_relationship" in resp['_status']['message']
        assert "updated" in resp['_status']['message']

        # Content - check only patched fields are updated
        sample_relationship = resp['results']
        fr = SampleRelationship.query.get(kf_id)
        for k, v in body.items():
            assert v == getattr(fr, k)
        # Unchanged
        assert sample_relationship["external_child_id"].startswith("SA")

    def test_delete(self):
        """
        Test delete an existing sample_relationship
        """
        _, rels = create_relationships()
        sr = rels[0]
        kf_id = sr.kf_id

        # Send get request
        response = self.client.delete(url_for(SAMPLE_RELATIONSHIPS_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())
        # Check status code
        assert response.status_code == 200

        # Check response body
        response = json.loads(response.data.decode("utf-8"))

        # Check database
        assert SampleRelationship.query.count() == 3

    def test_special_filter_param(self):
        """
        Test filter params

        /sample-relationships?sample_id
        /sample-relationships?study_id
        """
        # Add some sample relationships
        studies, rels = create_relationships()
        study_id = studies[0].kf_id

        # Case 1 - Query by study ID
        url = (
            url_for(SAMPLE_RELATIONSHIPS_LIST_URL) + f"?study_id={study_id}"
        )
        response = self.client.get(url, headers=self._api_headers())

        # Check response status code
        assert response.status_code == 200

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        assert len(content) == 2

        # Case 2 - Query by sample_id
        sample_id = rels[0].parent_id
        url = (
            url_for(SAMPLE_RELATIONSHIPS_LIST_URL) +
            f"?sample_id={sample_id}"
        )
        response = self.client.get(url, headers=self._api_headers())

        # Check response status code
        assert response.status_code == 200

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        assert len(content) == 1

        # Case 3 - Query by sample_id and other params
        sample_id = rels[0].parent_id
        url = (
            url_for(SAMPLE_RELATIONSHIPS_LIST_URL) +
            f"?sample_id={sample_id}&external_child_id=foo"
        )
        response = self.client.get(url, headers=self._api_headers())

        # Check response status code
        assert response.status_code == 200

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        assert len(content) == 0
