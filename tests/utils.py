import unittest
from dataservice import create_app
from dataservice.extensions import db

from tests.mocks import MockIndexd
from unittest.mock import patch, Mock

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


class IndexdTestCase(FlaskTestCase):
    """ Mocks out indexd for unittest style testing """

    def setUp(self):
        super(IndexdTestCase, self).setUp()
        self.indexd_patch = patch('dataservice.extensions.flask_indexd.requests')
        indexd_mock = MockIndexd()
        self.indexd = self.indexd_patch.start()
        self.indexd.Session().get.side_effect = indexd_mock.get
        self.indexd.Session().post.side_effect = indexd_mock.post

    def tearDown(self):
        super(IndexdTestCase, self).tearDown()
        self.indexd_patch.stop()
