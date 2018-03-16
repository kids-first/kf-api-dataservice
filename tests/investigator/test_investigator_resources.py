import json

from flask import url_for

from dataservice.api.investigator.models import Investigator 
from tests.utils import FlaskTestCase

INVESTIGATOR_URL = 'api.investigators'
INVESTIGATOR_LIST_URL = 'api.investigators_list'


class InvestigatorTest(FlaskTestCase):
    '''
    Test investigator api
    '''

    def test_post_investigator(self):
        '''
        Test creating a new investigator
        '''
        response = self._make_investigator(name='TEST')
        resp = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)

        self.assertIn('investigator', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])
        self.assertNotIn('_id', resp['results'])

        inv = Investigator.query.first()
        investigator = resp['results']
        self.assertEqual(inv.kf_id, investigator['kf_id'])
        self.assertEqual(inv.name, investigator['name'])

    def test_get_investigator(self):
        '''
        Test retrieving a investigator by id
        '''
        resp = self._make_investigator('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(INVESTIGATOR_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        investigator = resp['results']
        p = Investigator.query.first()
        self.assertEqual(kf_id, investigator['kf_id'])

    def test_patch_investigator(self):
        '''
        Test updating an existing investigator
        '''
        response = self._make_investigator(name='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        investigator = resp['results']
        kf_id = investigator.get('kf_id')
        name = investigator.get('name')

        # Update the investigator
        body = {
            'name': 'Updated-{}'.format(name),
        }
        response = self.client.patch(url_for(INVESTIGATOR_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Investigator.query.get(kf_id).name, body['name'])

        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('investigator', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        investigator = resp['results']
        self.assertEqual(investigator['kf_id'], kf_id)
        self.assertEqual(investigator['name'], body['name'])

    def test_delete_investigator(self):
        '''
        Test deleting a investigator by id
        '''
        resp = self._make_investigator('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(INVESTIGATOR_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url_for(INVESTIGATOR_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def _make_investigator(self, name='test'):
        '''
        Convenience method to create a investigator with a given name
        '''
        body = {
            'name': name
        }
        response = self.client.post(url_for(INVESTIGATOR_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response
