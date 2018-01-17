import json
import unittest
from dataservice import create_app
from dataservice.extensions import db
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

