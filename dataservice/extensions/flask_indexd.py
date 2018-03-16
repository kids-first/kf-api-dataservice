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

    def merge_properties(self, uuid, record):
        """
        Get an object from indexd by uuid and merge the object's properties
        onto the SQLAlchemy model instance

        :param uuid: UUID of indexd object
        :param record: SQLAlchemy model instance representing file-like object
        """
        resp = self.get(uuid)

        # Might want to use partial deserialization here
        for prop, v in resp.json().items():
            if hasattr(record, prop):
                setattr(record, prop, v)

        if 'metadata' in resp.json():
            record._metadata = resp.json()['metadata']

    def register_record(self, record):
        """
        Registers a new record with indexd.

        The response upon successful registry will contain a `did` which will
        be used as the target's uuid so that it may be joined with the indexd
        data.
        """
        if current_app.config['INDEXD_URL'] is None:
            return

        resp = self.create(record)

        # Update the records' uuid with the new did recieved from indexd
        record.uuid = resp['did']

        return record

    def delete_record(self, record):
        """
        Deletes a document in indexd
        """
        # Get the current revision if not already loaded
        if record.rev is None:
            self.merge_properties(record.uuid, record)

        self.delete(record)

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

    def create(self, record):
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

        :param record: SQLAlchemy model instance representing file-like object
        :returns: Non-error response from indexd
        :throws: Aborts on non-ok http code returned from indexd
        """
        req_body = {
            "file_name": record.file_name,
            "size": record.size,
            "form": "object",
            "hashes": {
                "md5": str(record.md5sum).replace('-', '')
            },
            "urls": [
                record.file_url
            ],
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
            abort(resp.status_code or 500, message)

        resp = resp.json()
        return resp

    def update(self, record):
        """
        Updates a record in indexd

        :param record: SQLAlchemy model instance representing file-like object
        :throws: Aborts on non-ok http code returned from indexd
        """
        # Fetch rev for the did
        if record.rev is None:
            r = self.session.get(current_app.config['INDEXD_URL']
                                 + record.uuid)
            try:
                r.raise_for_status()
            except HTTPError:
                abort(r.status_code or 500, 'could not update record')
            record.rev = r.json()['rev']

        req_body = {
            "file_name": record.file_name,
            "size": record.size,
            "hashes": {
                "md5": record.md5sum
            },
            "urls": [
                record.file_url
            ],
            "metadata": record._metadata
        }

        # Update the file on indexd
        url = '{}{}?rev={}'.format(current_app.config['INDEXD_URL'],
                                   record.uuid, record.rev)
        resp = self.session.put(url, json=req_body)

        try:
            resp.raise_for_status()
        except HTTPError:
            abort(resp.status_code or 500, 'could not update record')

    def delete(self, record):
        """
        Delete a record from indexd by did

        :param record: SQLAlchemy model instance representing file-like object
        :throws: Aborts on non-ok http code returned from indexd
        """
        if record.rev is None:
            r = self.session.get(current_app.config['INDEXD_URL']
                                 + record.uuid)
            # r.raise_for_status()
            record.rev = r.json()['rev']

        url = '{}{}?rev={}'.format(current_app.config['INDEXD_URL'],
                                   record.uuid, record.rev)
        print(self.session.delete)
        resp = self.session.delete(url)

        try:
            resp.raise_for_status()
        except HTTPError:
            abort(resp.status_code or 500,
                  'could not delete record: {}'.format(resp.json()))

    @property
    def session(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'indexd_session'):
                ctx.indexd_session = self.new_session()
            return ctx.indexd_session
