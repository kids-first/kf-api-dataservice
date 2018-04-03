import json
from datetime import datetime
from dateutil import parser, tz

from flask import url_for

from dataservice.extensions import db
from dataservice.api.family.models import Family
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

FAMILY_URL = 'api.families'
FAMILY_LIST_URL = 'api.families_list'


class FamilyTest(FlaskTestCase):
    """
    Test family api endpoints
    """

    def test_post_family(self):
        """
        Test creating a new family 
        """
        response = self._make_family(external_id='TEST000')
        resp = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)

        self.assertIn('family', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        family = resp['results']
        fam = Family.query.get(family['kf_id'])
        self.assertEqual(fam.external_id, family['external_id'])

    def test_get_family(self):
        """
        Test retrieving a family by id
        """
        resp = self._make_family('TESTXXX')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(FAMILY_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        family = resp['results']
        fam = Family.query.get(kf_id)
        self.assertEqual(kf_id, family['kf_id'])
        self.assertEqual(kf_id, fam.kf_id)
        self.assertEqual(fam.external_id, family['external_id'])

    def test_get_all_families(self):
        """
        Test retrieving all families 
        """
        self._make_family(external_id='TEST')

        response = self.client.get(url_for(FAMILY_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_patch_family(self):
        """
        Test updating an existing family 
        """
        orig = Family.query.count()
        response = self._make_family(external_id='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        family = resp['results']
        kf_id = family['kf_id']
        body = {
            'external_id': 'NEWID',
        }
        self.assertEqual(orig+1, Family.query.count())
        response = self.client.patch(url_for(FAMILY_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('family', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        fam = Family.query.get(kf_id)
        self.assertEqual(fam.external_id, resp['results']['external_id'])
        self.assertEqual(orig+1, Family.query.count())

    def test_delete_family(self):
        """
        Test deleting a family by id
        """
        orig = Family.query.count()
        resp = self._make_family('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(FAMILY_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Family.query.count(), orig)

        response = self.client.get(url_for(FAMILY_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def _make_family(self, external_id='TEST-0001'):
        """
        Create a new family with given external_id
        """
        # Make required entities first
        body = {
            'external_id': external_id,
        }
        response = self.client.post(url_for(FAMILY_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response
