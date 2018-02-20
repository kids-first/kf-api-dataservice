import uuid
from requests.exceptions import HTTPError


def mock_indexd_post(status_code=200):
    """ Generates a function to produce responses that mock indexd """

    def post(*args, **kwargs):
        """
        Mocks a response from POST /index/
        """
        resp = {
          'baseid': 'dc51eafd-1a7a-48ea-8800-3dfef5f9bd49',
          'did': str(uuid.uuid4()),
          'rev': '2e68e5f2'
        }

        class MockResp:
            status_code = 200

            def json(self):
                return resp

            def raise_for_status(self):
                if status_code != 200:
                    raise HTTPError('{} Client Error'.format(status_code), 500)
                return None

        mock_resp = MockResp()
        mock_resp.status_code = status_code
        return mock_resp

    return post


def mock_indexd_put(status_code=200):
    """ Generates a function to produce responses that mock indexd """

    def put(url, *args, **kwargs):
        """
        Mocks a response from POST /index/
        """
        did = url.split('/')[-1].split('?')[0]
        resp = {
          "baseid": "dc51eafd-1a7a-48ea-8800-3dfef5f9bd49",
          "created_date": "2018-02-21T00:44:27.414661",
          "did": did,
          "file_name": "hg38.bam",
          "form": "object",
          "hashes": {
            "md5": "dcff06ebb19bc9aa8f1aae1288d10dc2"
          },
          "metadata": {
            "acls": "INTERNAL"
          },
          "rev": "4e29e5fa",
          "size": 7696048,
          "updated_date": "2018-02-21T00:44:27.414671",
          "urls": [
            "s3://bucket/key"
          ],
          "version": None
        }

        class MockResp:
            status_code = 200

            def json(self):
                return resp

            def raise_for_status(self):
                if status_code != 200:
                    raise HTTPError('{} Client Error'.format(status_code), 500)
                return None

        return MockResp()

    return put


def mock_indexd_get(url, *args, **kwargs):
    """
    Mocks a response from GET /index/
    """
    did = url.split('/')[-1].split('?')[0]

    resp = {
      "baseid": "dc51eafd-1a7a-48ea-8800-3dfef5f9bd49",
      "created_date": "2018-02-21T00:44:27.414661",
      "did": did,
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

    class MockResp:
        status_code = 200

        def json(self):
            return resp

    return MockResp()
