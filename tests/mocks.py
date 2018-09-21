import uuid
import json
import pytest

from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError


class MockResp(MagicMock):
    def __init__(self, *args, resp={}, status_code=200, **kwargs):
        super(MockResp, self).__init__(*args, **kwargs)
        self.resp = resp
        self.status_code = status_code

    def json(self):
        return self.resp

    def data(self):
        return json.dumps(self.resp)

    def raise_for_status(self):
        if self.status_code != 200:
            raise HTTPError('{} Client Error'.format(self.status_code),
                            self.status_code)


class MockIndexd(MagicMock):
    """
    Mocks out common indexd service endpoints with templated responses

    - POST - create new document or version
    - GET - get info on a document or version by did
    """

    doc_base = {
        "file_name": "hg38.bam",
        "form": "object",
        "hashes": {
            "md5": "dcff06ebb19bc9aa8f1aae1288d10dc2"
        },
        "size": 7696048,
        "urls": [
            "s3://bucket/key"
        ],
    }

    doc = doc_base.copy()
    doc.update({
        "baseid": "dc51eafd-1a7a-48ea-8800-3dfef5f9bd49",
        "created_date": "2018-02-21T00:44:27.414661",
        "did": "",
        "metadata": {
        },
        "acl": ["INTERNAL"],
        "rev": "39b19b2d",
        "updated_date": "2018-02-21T00:44:27.414671",
        "version": None
    })

    # Need to store docs so new docs vs new versions can be differentiated
    baseid_by_did = {}

    def __init__(self, *args, status_code=200, **kwargs):
        super(MockIndexd, self).__init__(*args, **kwargs)
        self.status_code = status_code

    def post(self, url, *args, **kwargs):
        """
        Mocks a response from POST /index/ and POST /bulk/documents
        """

        resp = {
          'baseid': str(uuid.uuid4()),
          'did': str(uuid.uuid4()),
          'rev': str(uuid.uuid4())[:8]
        }

        did = url.split('/')[-1].split('?')[0]
        if len(did) == 56:
            # If there was a did in the url, assume it was an update
            resp['baseid'] = self.baseid_by_did['did']
        else:
            # Otherwise, assume creation of a new doc and track the baseid
            self.baseid_by_did[resp['did']] = resp['baseid']

        if 'bulk/documents' in url:
            resp = [resp]

        mock_resp = MockResp(resp=resp, status_code=self.status_code)
        return mock_resp

    def get(self, url, *args, **kwargs):
        """
        Mocks a response from GET /index/
        """
        if url.endswith('/versions'):
            did = url.split('/')[-2]
            resp = {}
            for i in range(3):
                resp[i] = self.doc.copy()
                resp[i]['did'] = did if i == 0 else str(uuid.uuid4())
        else:
            did = url.split('/')[-1].split('?')[0]
            resp = self.doc.copy()
            resp['did'] = did

        return MockResp(resp=resp, status_code=self.status_code)


@pytest.yield_fixture(scope='function')
def indexd(mocker):
    mock = mocker.patch('dataservice.extensions.flask_indexd.requests')
    indexd_mock = MockIndexd()
    mock.Session().get.side_effect = indexd_mock.get
    mock.Session().post.side_effect = indexd_mock.post
    yield mock.Session()
