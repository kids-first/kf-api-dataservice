import json
import unittest
from flask import current_app, url_for

from dataservice import db
from dataservice.model import Person
from utils import FlaskTestCase

PERSONS_PREFIX = 'persons'
NEW_PERSON_URL = '{}_{}'.format(PERSONS_PREFIX, 'new_person')
EXISTING_PERSON_URL = '{}_{}'.format(PERSONS_PREFIX, 'existing_person')
PERSONS_URL = '{}_{}'.format(PERSONS_PREFIX, 'persons')


class PersonTest(FlaskTestCase):
    """
    Test person api
    """

    def test_post_person(self):
        """
        Test creating a new person
        """
        response = self._make_person(external_id="TEST")
        self.assertEqual(response.status_code, 201)

        resp = json.loads(response.data.decode("utf-8"))
        self._test_response_content(resp, 201)

        self.assertEqual('person created', resp['message'])

        p = Person.query.first()
        person = resp['content']['persons'][0]
        self.assertEqual(p.kf_id, person['kf_id'])
        self.assertEqual(p.external_id, person['external_id'])

    def test_get_person(self):
        """
        Test retrieving a person by id
        """
        resp = self._make_person("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['content']['persons'][0]['kf_id']

        response = self.client.get(url_for(EXISTING_PERSON_URL,
                                           person_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self._test_response_content(resp, 200)

        person = resp['content']['persons'][0]

        self.assertEqual(kf_id, person['kf_id'])

    def test_get_all_persons(self):
        """
        Test retrieving all persons
        """
        self._make_person(external_id="MyTestPerson1")

        response = self.client.get(url_for(PERSONS_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('content')
        persons = content.get('persons')
        self.assertEqual(status_code, 200)
        self.assertIs(type(persons), list)
        self.assertEqual(len(persons), 1)

    def test_put_person(self):
        """
        Test updating an existing person
        """
        response = self._make_person(external_id="TEST")
        resp = json.loads(response.data.decode("utf-8"))
        person = resp['content']['persons'][0]
        kf_id = person.get('kf_id')
        external_id = person.get('external_id')

        body = {
            'external_id': 'Updated-{}'.format(external_id)
        }
        response = self.client.put(url_for(EXISTING_PERSON_URL,
                                           person_id=kf_id),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        self.assertEqual(response.status_code, 201)

        resp = json.loads(response.data.decode("utf-8"))
        self._test_response_content(resp, 201)
        self.assertEqual('person updated', resp['message'])

        p = Person.query.first()
        person = resp['content']['persons'][0]
        self.assertEqual(p.kf_id, person['kf_id'])
        self.assertEqual(p.external_id, person['external_id'])

    def test_delete_person(self):
        """
        Test deleting a person by id
        """
        resp = self._make_person("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['content']['persons'][0]['kf_id']

        response = self.client.delete(url_for(EXISTING_PERSON_URL,
                                           person_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url_for(EXISTING_PERSON_URL,
                                           person_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 404)

    def _make_person(self, external_id="TEST-0001"):
        """
        Convenience method to create a person with a given source name
        """
        body = {
            'external_id': external_id
        }
        response = self.client.post(url_for(NEW_PERSON_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))

        return response

    def _test_response_content(self, resp, status_code):
        """
        Test that response body has expected fields
        """
        self.assertIn('content', resp)
        self.assertIn('message', resp)
        self.assertIn('status', resp)
        self.assertEqual(resp['status'], status_code)