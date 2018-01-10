import json
import unittest
from dataservice import create_app, db
from flask import url_for


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _api_headers(self):
        return {
          "Accept": "application/json",
          "Content-Type": "application/json"
        }

    def _make_person(self, source_name="TEST-0001"):
        """
        Make a person with a given source name
        """
        body = {
            'source_name': source_name
        }
        response = self.client.put(url_for('person_person', person_id='1'),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))

        return response
