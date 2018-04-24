import unittest
from dataservice import create_app
from dataservice.extensions import db

from tests.mocks import MockIndexd
from unittest.mock import patch, Mock


class WithBucketService():
    """ Mocks responses from the bucket service """

    def setUpBucketMock(self):
        mod = 'dataservice.api.study.models.requests'
        self.patch_bucket_service = patch(mod)
        self.bucket_service = self.patch_bucket_service.start()
        
        mock_resp_get = Mock()
        mock_resp_get.status_code = 200
        mock_resp_post = Mock()
        mock_resp_post.status_code = 201

        self.bucket_service.Session().get.side_effect = mock_resp_get
        self.bucket_service.Session().post.side_effect = mock_resp_post

    def tearDownBucketMock(self):
        self.bucket_service.stop()


class FlaskTestCase(unittest.TestCase, WithBucketService):

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.setUpBucketMock()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

        self.app_context.pop()
        self.tearDownBucketMock()

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
