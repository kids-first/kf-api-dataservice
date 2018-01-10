import json
import unittest
from flask import current_app, url_for

from dataservice import db
from dataservice.model import Person

from utils import FlaskTestCase


class PersonTest(FlaskTestCase):
    """
    Test database model
    """

    def test_put_person(self):
        """
        Test that a person is created correctly
        """

        body = {
            'source_name': 'test_person_1'
        }
        response = self.client.put(url_for('person_person', person_id='1'),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))

        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 201)
        self.assertIn('content', resp)
        self.assertIn('message', resp)
        self.assertIn('status', resp)
        self.assertEqual(resp['status'], 201)
        self.assertEqual(resp['status'], 201)
        self.assertEqual('person created', resp['message'])

        self.assertEqual(Person.query.count(), 1)
        p = Person.query.first()
        self.assertEqual(p.kf_id, resp['content']['kf_id'])
        self.assertEqual(p.source_name, resp['content']['source_name'])

    def test_get_person(self):
        """
        Test retrieving a person by id
        """
        resp = self._make_person("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['content']['kf_id']

        response = self.client.get(url_for('person_person', person_id=kf_id),
                                   headers=self._api_headers())
