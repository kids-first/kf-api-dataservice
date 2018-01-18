import json
from flask import url_for

from dataservice.api.person.models import Person
from tests.utils import FlaskTestCase

PERSONS_PREFIX = 'api.persons'
PERSON_URL = '{}_{}'.format(PERSONS_PREFIX, 'person')
PERSON_LIST_URL = '{}_{}'.format(PERSONS_PREFIX, 'person_list')


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

        self.assertEqual('person created', resp['_status']['message'])

        p = Person.query.first()
        person = resp['results'][0]
        self.assertEqual(p.kf_id, person['kf_id'])
        self.assertEqual(p.external_id, person['external_id'])

    def test_get_not_found(self):
        """
        Test get person that does not exist
        """
        kf_id = 'non_existent'
        response = self.client.get(url_for(PERSON_URL, kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self._test_response_content(resp, 404)
        message = "person with kf_id '{}' not found".format(kf_id)
        self.assertIn(message, resp['_status']['message'])

    def test_get_person(self):
        """
        Test retrieving a person by id
        """
        resp = self._make_person("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results'][0]['kf_id']

        response = self.client.get(url_for(PERSON_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self._test_response_content(resp, 200)

        person = resp['results'][0]

        self.assertEqual(kf_id, person['kf_id'])

    def test_get_all_persons(self):
        """
        Test retrieving all persons
        """
        self._make_person(external_id="MyTestPerson1")

        response = self.client.get(url_for(PERSON_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_put_person(self):
        """
        Test updating an existing person
        """
        response = self._make_person(external_id="TEST")
        resp = json.loads(response.data.decode("utf-8"))
        person = resp['results'][0]
        kf_id = person.get('kf_id')
        external_id = person.get('external_id')

        body = {
            'external_id': 'Updated-{}'.format(external_id)
        }
        response = self.client.put(url_for(PERSON_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        self.assertEqual(response.status_code, 201)

        resp = json.loads(response.data.decode("utf-8"))
        self._test_response_content(resp, 201)
        self.assertEqual('person updated', resp['_status']['message'])

        p = Person.query.first()
        person = resp['results'][0]
        self.assertEqual(p.kf_id, person['kf_id'])
        self.assertEqual(p.external_id, person['external_id'])

    def test_delete_person(self):
        """
        Test deleting a person by id
        """
        resp = self._make_person("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results'][0]['kf_id']

        response = self.client.delete(url_for(PERSON_URL,
                                              kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url_for(PERSON_URL,
                                           kf_id=kf_id),
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
        response = self.client.post(url_for(PERSON_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))

        return response

    def _test_response_content(self, resp, status_code):
        """
        Test that response body has expected fields
        """
        self.assertIn('results', resp)
        self.assertIn('_status', resp)
        self.assertIn('message', resp['_status'])
        self.assertEqual(resp['_status']['code'], status_code)
