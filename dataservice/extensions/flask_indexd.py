import requests
import uuid

from flask import current_app, abort
from flask import _app_ctx_stack as stack
from requests.exceptions import HTTPError


class RecordNotFound(HTTPError):
    """ Could not find the record in indexd """


class Indexd(object):
    """
    Indexd flask extension for interacting with the Gen3 Indexd service
    """

    def __init__(self, app=None):
        self.app = app
        # Used to store documents prefetched for a page
        self.page_cache = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('INDEXD_URL', None)
        self.url = app.config['INDEXD_URL']
        if self.url:
            self.bulk_url = '/'.join(self.url.split('/')[:-1] + ['bulk/'])
        else:
            self.bulk_url = None
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def new_session(self):
        """ Preconfigure a session """
        s = requests.Session()
        s.auth = (current_app.config['INDEXD_USER'],
                  current_app.config['INDEXD_PASS'])
        s.headers.update({'Content-Type': 'application/json',
                          'User-Agent': 'Kids First Dataservice'})
        return s

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'indexd_session'):
            ctx.indexd_session.close()

    def prefetch(self, dids):
        """
        Fetch a list of documents by did into the page cache.
        """
        # If running in dev mode, don't call indexd
        if self.url is None or self.bulk_url is None:
            return
        resp = self.session.post(self.bulk_url + 'documents', json=dids).json()
        for doc in resp:
            self.page_cache[doc['did']] = doc

    def clear_cache(self):
        self.page_cache = {}

    def get(self, record):
        """
        Retrieves a record from indexd

        :param record: The record object
        :returns: Non-error response from indexd
        :throws: Aborts on non-ok http code returned from indexd
        :throws: RecordNotFound if record does not exist in indexd
        """
        # If running in dev mode, don't call indexd
        if self.url is None:
            return record

        if record.latest_did in self.page_cache:
            return self.page_cache[record.latest_did]

        url = self.url + record.latest_did
        resp = self.session.get(url)
        self.check_response(resp)
        resp.raise_for_status()

        # update fields on the target record's object
        for prop, v in resp.json().items():
            if hasattr(record, prop):
                if prop == 'metadata':
                    record._metadata = v
                else:
                    setattr(record, prop, v)

        return record

    def new(self, record):
        """
        Registers a new record in indexd

        Sends post with a body containing info about the file:

          {
            "file_name": "my_file",
            "acl": ["phs000000"],
            "hashes": {
              "md5": "0b7940593044dff8e74380476b2b27a9"
            },
            "size": 123,
            "urls": [
              "s3://mybucket/mykey/"
            ],
            "metadata": {
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
        # If running in dev mode, dont call indexd
        if self.url is None:
            record.uuid = str(uuid.uuid4())
            record.latest_did = str(uuid.uuid4())
            return record

        meta = record._metadata

        req_body = {
            "file_name": record.file_name,
            "size": record.size,
            "form": "object",
            "hashes": record.hashes,
            "acl": record.acl,
            "urls": record.urls,
            "metadata": meta
        }

        # Register the file on indexd
        resp = self.session.post(self.url,
                                 json=req_body)

        resp.raise_for_status()
        resp = resp.json()

        # Update the record object with the id fields
        record.uuid = resp['baseid']
        record.latest_did = resp['did']

        return record

    def update(self, record):
        """
        Updates a record in indexd

        :param record: A file-like object
        """
        # If running in dev mode, dont call indexd
        if self.url is None:
            record.latest_did = str(uuid.uuid4())
            return record

        # Fetch rev for the did
        url = self.url + record.latest_did
        resp = self.session.get(url)
        self.check_response(resp)

        old = resp.json()
        record.rev = old['rev']

        req_body = {
            "file_name": record.file_name,
            "size": record.size,
            "hashes": record.hashes,
            "acl": record.acl,
            "urls": record.urls,
            "metadata": record._metadata
        }

        if (req_body['size'] == old['size'] and
           req_body['hashes'] == old['hashes']):
            del req_body['size']
            del req_body['hashes']

        # If acl changed, update all previous version with new acl
        if record.acl != old['acl']:
            self._update_all_acls(record)

        url = '{}{}?rev={}'.format(self.url, record.latest_did,
                                   record.rev)
        if 'size' in req_body or 'hashes' in req_body:
            # Create a new version in indxed
            req_body['form'] = 'object'
            resp = self.session.post(url, json=req_body)
            did = resp.json()['did']
            record.latest_did = did
        else:
            # Update the file on indexd
            resp = self.session.put(url, json=req_body)

        self.check_response(resp)
        resp.raise_for_status()

        return record

    def _update_all_acls(self, record):
        """
        Update acls for all previous versions of a record and update the
        target record's rev
        """
        # Only use fields allowed by the indexd PUT schema
        fields = ['urls', 'acl', 'file_name', 'version',
                  'metadata', 'urls_metadata', 'rev']

        url = '{}{}/versions'.format(self.url, record.latest_did)
        versions = self.session.get(url).json()
        for version, doc in versions.items():
            if doc['acl'] != record.acl:
                did = doc['did']
                doc = {k: v for k, v in doc.items() if k in fields}
                doc['acl'] = record.acl
                if doc['version'] is None:
                    del doc['version']
                url = '{}{}?rev={}'.format(self.url, did, doc['rev'])
                # rev is not allowed in put schema
                del doc['rev']
                resp = self.session.put(url, json=doc)
                # Update the record's rev if it's the record being modified
                if record.latest_did == did:
                    record.rev = resp.json()['rev']

    def delete(self, record):
        """
        Delete a record from indexd by did

        :param record: A file-like object
        :throws: Aborts on non-ok http code returned from indexd
        """
        # If running in dev mode, dont call indexd
        if self.url is None:
            return record

        if record.rev is None:
            r = self.session.get(self.url + record.latest_did)
            record.rev = r.json()['rev']

        url = '{}{}?rev={}'.format(self.url, record.latest_did, record.rev)
        resp = self.session.delete(url)
        self.check_response(resp)
        try:
            resp.raise_for_status()
        except HTTPError:
            message = 'could not get file record'
            # Attach indexd error message, if there is one
            if 'error' in resp.json():
                message = '{}: {}'.format(message, resp.json()['error'])
            abort(resp.status_code, message)

        return record

    def check_response(self, resp):
        """
        Validate a response from indexd and throw any necessary exceptions
        """
        if (resp.status_code == 404 and
                'error' in resp.json() and
                resp.json()['error'] == 'no record found'):
            raise RecordNotFound()

    @property
    def session(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'indexd_session'):
                ctx.indexd_session = self.new_session()
            return ctx.indexd_session
