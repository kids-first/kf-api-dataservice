import requests

from flask import current_app, abort
from flask import _app_ctx_stack as stack
from requests.exceptions import HTTPError


class Indexd(object):
    """
    Indexd flask extension for interacting with the Gen3 Indexd service
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('INDEXD_URL', None)
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def new_session(self):
        """ Preconfigure a session """
        s = requests.Session()
        s.auth = (current_app.config['INDEXD_USER'],
                  current_app.config['INDEXD_PASS'])
        s.headers.update({'Content-Type': 'application/json'})
        return s

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'indexd_session'):
            ctx.indexd_session.close()

    def get(self, did):
        """
        Retrieves a record from indexd

        :param did: The did to fetch from indexd
        :returns: Non-error response from indexd
        :throws: Aborts on non-ok http code returned from indexd
        """
        resp = self.session.get(current_app.config['INDEXD_URL'] + did)

        try:
            resp.raise_for_status()
        except HTTPError:
            message = 'could not get file record'
            # Attach indexd error message, if there is one
            if 'error' in resp.json():
                message = '{}: {}'.format(message, resp.json()['error'])
            abort(resp.status_code, message)

        return resp

    def new(self, record):
        """
        Registers a new record in indexd

        Sends post with a body containing info about the file:

          {
            "file_name": "my_file",
            "hashes": {
              "md5": "0b7940593044dff8e74380476b2b27a9"
            },
            "size": 123,
            "urls": [
              "s3://mybucket/mykey/"
            ],
            "metadata": {
              "acls": "phs000000",
              "kf_id": "PT_00000000"
            }
          }

        A successful response from indexd should contain the following:

          {
            "baseid": <some-uuid>,
            "did": <some-uuid",
            "rev": <first-8-char-of-a-uuid>
          }

        :param record: A file-like object
        :returns: Non-error response from indexd
        :throws: Aborts on non-ok http code returned from indexd
        """
        req_body = {
            "file_name": record.file_name,
            "size": record.size,
            "form": "object",
            "hashes": record.hashes,
            "urls": record.urls,
            "metadata": record._metadata
        }

        # Register the file on indexd
        resp = self.session.post(current_app.config['INDEXD_URL'],
                                 json=req_body)

        try:
            resp.raise_for_status()
        except HTTPError:
            message = 'could not register record'
            # Attach indexd error message, if there is one
            if 'error' in resp.json():
                message = '{}: {}'.format(message, resp.json()['error'])
            abort(resp.status_code, message)

        resp = resp.json()
        return resp

    def update(self, record):
        """
        Updates a record in indexd

        :param record: A file-like object
        :throws: Aborts on non-ok http code returned from indexd
        """
        # Fetch rev for the did
        r = self.session.get(current_app.config['INDEXD_URL']+record.uuid)
        r.raise_for_status()
        record.rev = r.json()['rev']

        req_body = {
            "file_name": record.file_name,
            "size": record.size,
            "hashes": record.hashes,
            "urls": record.urls,
            "metadata": record._metadata
        }

        # Update the file on indexd
        url = '{}{}?rev={}'.format(current_app.config['INDEXD_URL'],
                                   record.uuid, record.rev)
        resp = self.session.put(url, json=req_body)

        try:
            resp.raise_for_status()
        except HTTPError:
            abort(resp.status_code, 'could not update record')

    def delete(self, record):
        """
        Delete a record from indexd by did

        :param record: A file-like object
        :throws: Aborts on non-ok http code returned from indexd
        """
        if record.rev is None:
            r = self.session.get(self.url + record.latest_did)
            # r.raise_for_status()
            record.rev = r.json()['rev']

        url = '{}{}?rev={}'.format(self.url, record.latest_did, record.rev)
        resp = self.session.delete(url)

        try:
            resp.raise_for_status()
        except HTTPError:
            message = 'could not delete record'
            if 'error' in resp.json():
                message += ': {}'.format(resp.json()['error'])
            abort(resp.status_code, message)

    @property
    def session(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'indexd_session'):
                ctx.indexd_session = self.new_session()
            return ctx.indexd_session
