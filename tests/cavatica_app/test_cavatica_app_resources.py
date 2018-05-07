import json
from datetime import datetime
from dateutil import parser, tz

from flask import url_for

from dataservice.api.cavatica_app.models import CavaticaApp
from tests.utils import FlaskTestCase

CAVATICA_APP_URL = 'api.cavatica_apps'
CAVATICA_APP_LIST_URL = 'api.cavatica_apps_list'


class CavaticaAppTest(FlaskTestCase):
    """
    Test cavatica_app api endpoints
    """

    def test_post_cavatica_app(self):
        """
        Test creating a new cavatica_app
        """
        response = self._make_cavatica_app(name='app1')
        resp = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)

        self.assertIn('cavatica_app', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        cavatica_app = resp['results']
        app = CavaticaApp.query.get(cavatica_app['kf_id'])
        self.assertEqual(app.name, cavatica_app['name'])

    def test_get_cavatica_app(self):
        """
        Test retrieving a cavatica_app by id
        """
        resp = self._make_cavatica_app('app1')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(CAVATICA_APP_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        cavatica_app = resp['results']
        app = CavaticaApp.query.get(kf_id)
        self.assertEqual(kf_id, cavatica_app['kf_id'])
        self.assertEqual(kf_id, app.kf_id)
        self.assertEqual(app.name, cavatica_app['name'])
        self.assertEqual(app.revision, cavatica_app['revision'])
        self.assertEqual(app.github_commit_url,
                         cavatica_app['github_commit_url'])

    def test_get_all_cavatica_apps(self):
        """
        Test retrieving all cavatica_apps
        """
        self._make_cavatica_app(name='TEST')

        response = self.client.get(url_for(CAVATICA_APP_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_patch_cavatica_app(self):
        """
        Test updating an existing cavatica_app
        """
        orig = CavaticaApp.query.count()
        response = self._make_cavatica_app(name='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        cavatica_app = resp['results']
        kf_id = cavatica_app['kf_id']
        body = {
            'name': 'new name',
        }
        self.assertEqual(orig + 1, CavaticaApp.query.count())
        response = self.client.patch(url_for(CAVATICA_APP_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('cavatica_app', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        app = CavaticaApp.query.get(kf_id)
        self.assertEqual(app.name, resp['results']['name'])
        self.assertEqual(orig + 1, CavaticaApp.query.count())

    def test_delete_cavatica_app(self):
        """
        Test deleting a cavatica_app by id
        """
        orig = CavaticaApp.query.count()
        resp = self._make_cavatica_app('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(CAVATICA_APP_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CavaticaApp.query.count(), orig)

        response = self.client.get(url_for(CAVATICA_APP_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def _make_cavatica_app(self, name='app1'):
        """
        Create a new cavatica_app with given name
        """
        url = ('https://github.com/kids-first/kf-alignment-cavatica_task/'
               'commit/0d7f93dff6463446b0ed43dc2883f60c28e6f1f4')
        body = {
            'name': name,
            'revision': 0,
            'external_cavatica_app_id': name + '_id',
            'github_commit_url': url
        }
        response = self.client.post(url_for(CAVATICA_APP_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response
