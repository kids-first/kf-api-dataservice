import json

from flask import url_for

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.investigator.models import Investigator
from tests.utils import FlaskTestCase

STUDY_URL = 'api.studies'
STUDY_LIST_URL = 'api.studies_list'


class StudyTest(FlaskTestCase):
    """
    Test study api endopoints
    """

    def test_post_study(self):
        """
        Test creating a new study
        """
        response = self._make_study(external_id='TEST')
        resp = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)

        self.assertIn('study', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])
        self.assertNotIn('_id', resp['results'])

        s = Study.query.first()
        study = resp['results']
        self.assertEqual(s.kf_id, study['kf_id'])
        self.assertEqual(s.external_id, study['external_id'])

    def test_get_study(self):
        """
        Test retrieving a study by id
        """
        resp = self._make_study('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(STUDY_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        study = resp['results']
        self.assertEqual(kf_id, study['kf_id'])

    def test_get_study_no_investigator(self):
        """
        Test that the investigator link is set to null
        if the study doesnt have an investigator
        """
        resp = self._make_study(include_nullables=False)
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(STUDY_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

        self.assertTrue('investigator' in resp['_links'])
        self.assertIs(None, resp['_links']['investigator'])

    def test_patch_study(self):
        """
        Test updating an existing study
        """
        response = self._make_study(external_id='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        study = resp['results']
        kf_id = study.get('kf_id')
        external_id = study.get('external_id')

        # Update the study via http api
        body = {
            'external_id': 'new_id',
            'release_status': 'Pending'
        }
        response = self.client.patch(url_for(STUDY_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Study.query.get(kf_id).external_id,
                         body['external_id'])

        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('study', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        study = resp['results']
        self.assertEqual(study['kf_id'], kf_id)
        self.assertEqual(study['external_id'], body['external_id'])
        self.assertEqual(study['release_status'], body['release_status'])

    def test_patch_study_no_required_field(self):
        """
        Test that we may update the study without a required field
        """
        response = self._make_study(external_id='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        study = resp['results']
        kf_id = study.get('kf_id')
        external_id = study.get('external_id')

        # Update the study via http api
        body = {
            'version': '2.0'
        }
        response = self.client.patch(url_for(STUDY_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Study.query.get(kf_id).version, '2.0')

        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('study', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        study = resp['results']
        self.assertEqual(study['kf_id'], kf_id)
        self.assertEqual(study['external_id'], external_id)
        self.assertEqual(study['version'], body['version'])

    def test_delete_study(self):
        """
        Test deleting a study by id
        """
        resp = self._make_study('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(STUDY_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url_for(STUDY_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def test_parent_study_id(self):
        """
        Test creating / updating a study with a parent study ID
        """
        # Parent study
        response = self._make_study(
            external_id='parent'
        )
        resp = json.loads(response.data.decode('utf-8'))
        kf_id = resp["results"]["kf_id"]

        # Create study with parent study ID
        response = self._make_study(
            external_id='child', parent_study_id=kf_id
        )
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 201)

        # Check results
        study = resp['results']
        self.assertEqual(study['parent_study_id'], kf_id)

        # Update parent study ID to study ID that does not exist
        body = {
            "parent_study_id": "SD_11111111"
        }
        child_study_id = study["kf_id"]
        response = self.client.patch(url_for(STUDY_URL,
                                             kf_id=child_study_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.data.decode('utf-8'))
        assert "does not exist" in resp["_status"]["message"]

        # Update parent study ID to invalid format
        body = {
            "parent_study_id": "foo"
        }
        child_study_id = study["kf_id"]
        response = self.client.patch(url_for(STUDY_URL,
                                             kf_id=child_study_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        self.assertEqual(response.status_code, 400)

    def _make_study(self, include_nullables=True, **kwargs):
        """
        Convenience method to create a study with a given source name
        """
        inv = Investigator(name='donald duck')
        db.session.add(inv)
        db.session.flush()

        body = {
            'external_id': "TEST",
            'version': '1.0',
            'release_status': 'Pending',
            'short_code': 'KF-ST0',
            'program': 'Kids First',
            'domain': 'Cancer',
            'biobank_name': 'CBTN Biobank',
            'biobank_email': 'research@cbtn.org',
        }
        body.update(kwargs)
        if include_nullables:
            body.update({'investigator_id': inv.kf_id})

        response = self.client.post(url_for(STUDY_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response
