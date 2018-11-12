import uuid
import json

from flask import url_for

from dataservice.extensions import db
from dataservice.api.cavatica_task.models import CavaticaTask
from dataservice.api.cavatica_app.models import CavaticaApp
from tests.utils import FlaskTestCase

CAVATICA_TASK_URL = 'api.cavatica_tasks'
CAVATICA_TASK_LIST_URL = 'api.cavatica_tasks_list'


class CavaticaTaskTest(FlaskTestCase):
    """
    Test cavatica_task api endpoints
    """

    def test_post_cavatica_task(self):
        """
        Test creating a new cavatica_task
        """
        response = self._make_cavatica_task(name='task1')
        resp = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)

        self.assertIn('cavatica_task', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        cavatica_task = resp['results']
        task = CavaticaTask.query.get(cavatica_task['kf_id'])
        self.assertEqual(task.name, cavatica_task['name'])

    def test_get_cavatica_task(self):
        """
        Test retrieving a cavatica_task by id
        """
        resp = self._make_cavatica_task('task1')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(CAVATICA_TASK_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        cavatica_task = resp['results']
        task = CavaticaTask.query.get(kf_id)
        self.assertEqual(kf_id, cavatica_task['kf_id'])
        self.assertEqual(kf_id, task.kf_id)
        self.assertEqual(task.name, cavatica_task['name'])

    def test_get_all_cavatica_tasks(self):
        """
        Test retrieving all cavatica_tasks
        """
        self._make_cavatica_task(name='TEST')

        response = self.client.get(url_for(CAVATICA_TASK_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_patch_cavatica_task(self):
        """
        Test updating an existing cavatica_task
        """
        orig = CavaticaTask.query.count()
        response = self._make_cavatica_task(name='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        cavatica_task = resp['results']
        kf_id = cavatica_task['kf_id']
        body = {
            'name': 'new name',
        }
        self.assertEqual(orig + 1, CavaticaTask.query.count())
        response = self.client.patch(url_for(CAVATICA_TASK_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('cavatica_task', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        task = CavaticaTask.query.get(kf_id)
        self.assertEqual(task.name, resp['results']['name'])
        self.assertEqual(orig + 1, CavaticaTask.query.count())

    def test_delete_cavatica_task(self):
        """
        Test deleting a cavatica_task by id
        """
        orig = CavaticaTask.query.count()
        resp = self._make_cavatica_task('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(CAVATICA_TASK_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CavaticaTask.query.count(), orig)

        response = self.client.get(url_for(CAVATICA_TASK_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def _make_cavatica_task(self, name='task1'):
        """
        Create a new cavatica_task with given name
        """
        data = {
            'external_cavatica_app_id': 'app1',
            'name': 'ImAwsammmmm',
            'revision': 1,
        }
        app = CavaticaApp(**data)
        db.session.add(app)
        db.session.commit()
        body = {
            'name': name,
            'external_cavatica_task_id': str(uuid.uuid4()),
            'cavatica_app_id': app.kf_id
        }
        response = self.client.post(url_for(CAVATICA_TASK_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response
