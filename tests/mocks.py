import uuid
from unittest.mock import MagicMock
from requests.exceptions import HTTPError


class MockResp(MagicMock):
    def __init__(self, *args, resp={}, status_code=200, **kwargs):
        super(MockResp, self).__init__(*args, **kwargs)
        self.resp = resp
        self.status_code = status_code

    def json(self):
        return self.resp

    def raise_for_status(self):
        if self.status_code != 200:
            raise HTTPError('{} Client Error'.format(self.status_code),
                            self.status_code)


class MockIndexd(MagicMock):

    doc = {
        "baseid": "dc51eafd-1a7a-48ea-8800-3dfef5f9bd49",
        "created_date": "2018-02-21T00:44:27.414661",
        "did": "",
        "file_name": "hg38.bam",
        "form": "object",
        "hashes": {
            "md5": "dcff06ebb19bc9aa8f1aae1288d10dc2"
        },
        "metadata": {
            "acls": "INTERNAL"
        },
        "rev": "39b19b2d",
        "size": 7696048,
        "updated_date": "2018-02-21T00:44:27.414671",
        "urls": [
            "s3://bucket/key"
        ],
        "version": None
    }

    def __init__(self, *args, status_code=200, **kwargs):
        super(MockIndexd, self).__init__(*args, **kwargs)
        self.status_code = status_code


    def post(self, *args, **kwargs):
        """
        Mocks a response from POST /index/
        """
        resp = {
          'baseid': 'dc51eafd-1a7a-48ea-8800-3dfef5f9bd49',
          'did': str(uuid.uuid4()),
          'rev': '2e68e5f2'
        }
        mock_resp = MockResp(resp=resp, status_code=self.status_code)
        return mock_resp

    def get(self, url, *args, **kwargs):
        """
        Mocks a response from GET /index/
        """
        did = url.split('/')[-1].split('?')[0]
        resp = self.doc.copy()
        resp['did'] = did

        return MockResp(resp=resp, status_code=self.status_code)

    def patch(self, url, *args, **kwargs):
        """
        Mocks a response from POST /index/
        """
        did = url.split('/')[-1].split('?')[0]
        resp = self.doc.copy()
        resp['did'] = did

        return MockResp(resp=resp, status_code=self.status_code)
