import uuid
import json

from flask import url_for

from dataservice.extensions import db
from dataservice.api.task.models import Task
from dataservice.api.cavatica_app.models import CavaticaApp
from tests.utils import FlaskTestCase

TASK_URL = 'api.tasks'
TASK_LIST_URL = 'api.tasks_list'


class TaskTest(FlaskTestCase):
    """
    Test task api endpoints
    """

    def test_post_task(self):
        """
        Test creating a new task
        """
        response = self._make_task(name='task1')
        resp = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)

        self.assertIn('task', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        task = resp['results']
        t = Task.query.get(task['kf_id'])
        self.assertEqual(t.name, task['name'])

    def test_get_task(self):
        """
        Test retrieving a task by id
        """
        resp = self._make_task('task1')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(TASK_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        task = resp['results']
        t = Task.query.get(kf_id)
        self.assertEqual(kf_id, task['kf_id'])
        self.assertEqual(kf_id, t.kf_id)
        self.assertEqual(t.name, task['name'])

    def test_get_all_tasks(self):
        """
        Test retrieving all tasks
        """
        self._make_task(name='TEST')

        response = self.client.get(url_for(TASK_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_patch_task(self):
        """
        Test updating an existing task
        """
        orig = Task.query.count()
        response = self._make_task(name='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        task = resp['results']
        kf_id = task['kf_id']
        body = {
            'name': 'new name',
        }
        self.assertEqual(orig + 1, Task.query.count())
        response = self.client.patch(url_for(TASK_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('task', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        task = Task.query.get(kf_id)
        self.assertEqual(task.name, resp['results']['name'])
        self.assertEqual(orig + 1, Task.query.count())

    def test_delete_task(self):
        """
        Test deleting a task by id
        """
        orig = Task.query.count()
        resp = self._make_task('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(TASK_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.query.count(), orig)

        response = self.client.get(url_for(TASK_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def _make_task(self, name='task1'):
        """
        Create a new task with given name
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
            'external_task_id': str(uuid.uuid4()),
            'cavatica_app_id': app.kf_id
        }
        response = self.client.post(url_for(TASK_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response
