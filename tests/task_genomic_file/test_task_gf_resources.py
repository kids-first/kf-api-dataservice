import uuid
import json
from flask import url_for

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.task.models import (
    Task,
    TaskGenomicFile
)
from tests.utils import FlaskTestCase

from unittest.mock import patch
from tests.mocks import MockIndexd

TASK_GF_URL = 'api.task_genomic_files'
TASK_GF_LIST_URL = 'api.task_genomic_files_list'


@patch('dataservice.extensions.flask_indexd.requests')
class TaskGenomicFileTest(FlaskTestCase):
    """
    Test task_genomic_file api endpoints
    """

    def test_post_task_genomic_file(self, mock):
        """
        Test creating a new task_genomic_file
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        response = self._make_task_genomic_file(mock)
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('task_genomic_file', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        # Content check
        task_genomic_file = resp['results']
        tgf = TaskGenomicFile.query.get(
            task_genomic_file['kf_id'])
        self.assertEqual(tgf.is_input, task_genomic_file['is_input'])

        # Relations check
        t_kfid = resp['_links']['task'].split('/')[-1]
        gf_kfid = resp['_links']['genomic_file'].split('/')[-1]
        assert tgf.task_id == t_kfid
        assert tgf.genomic_file_id == gf_kfid
        assert Task.query.get(t_kfid) is not None
        assert GenomicFile.query.get(gf_kfid) is not None

    def test_get_task_genomic_file(self, mock):
        """
        Test retrieving a task_genomic_file by id
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        resp = self._make_task_genomic_file(mock)
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(TASK_GF_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        task_genomic_file = resp['results']
        tgf = TaskGenomicFile.query.get(kf_id)
        self.assertEqual(kf_id, task_genomic_file['kf_id'])
        self.assertEqual(kf_id, tgf.kf_id)
        self.assertEqual(tgf.is_input, task_genomic_file['is_input'])

    def test_get_all_task_genomic_files(self, mock):
        """
        Test retrieving all task_genomic_files
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        self._make_task_genomic_file(mock)

        response = self.client.get(url_for(TASK_GF_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_patch_task_genomic_file(self, mock):
        """
        Test updating an existing task_genomic_file
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        response = self._make_task_genomic_file(mock)
        orig = TaskGenomicFile.query.count()
        resp = json.loads(response.data.decode('utf-8'))
        task_genomic_file = resp['results']
        kf_id = task_genomic_file['kf_id']
        body = {
            'is_input': not task_genomic_file['is_input'],
        }
        self.assertEqual(orig, TaskGenomicFile.query.count())
        response = self.client.patch(url_for(TASK_GF_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        resp = json.loads(response.data.decode('utf-8'))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        self.assertIn('task_genomic_file', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        task = TaskGenomicFile.query.get(kf_id)
        self.assertEqual(task.is_input, resp['results']['is_input'])
        self.assertEqual(orig, TaskGenomicFile.query.count())

    def test_delete_task_genomic_file(self, mock):
        """
        Test deleting a task_genomic_file by id
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        resp = self._make_task_genomic_file(mock)
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(TASK_GF_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TaskGenomicFile.query.count(), 0)

        response = self.client.get(url_for(TASK_GF_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def _create_task(self, _name, genomic_files=None):
        """
        Create task
        """
        data = {
            'external_task_id': str(uuid.uuid4()),
            'name': _name,
        }
        if genomic_files:
            data['genomic_files'] = genomic_files
        return Task(**data)

    def _create_entities(self):
        """
        Create participant with required entities
        """
        # Sequencing center
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()

        # Create study
        study = Study(external_id='phs001')

        # Participants
        p = Participant(external_id='p0',
                        is_proband=True,
                        study=study)

        # Biospecimen
        bs = Biospecimen(analyte_type='dna',
                         sequencing_center=sc,
                         participant=p)

        # SequencingExperiment
        data = {
            'external_id': 'se',
            'experiment_strategy': 'wgs',
            'is_paired_end': True,
            'platform': 'platform',
            'sequencing_center': sc
        }
        se = SequencingExperiment(**data)

        # Genomic Files
        genomic_files = []
        for i in range(4):
            data = {
                'file_name': 'gf_{}'.format(i),
                'data_type': 'submitted aligned read',
                'file_format': '.cram',
                'urls': ['s3://file_{}'.format(i)],
                'hashes': {'md5': str(uuid.uuid4())},
                'is_harmonized': True if i % 2 else False
            }
            gf = GenomicFile(**data)
            bs.genomic_files.append(gf)
            se.genomic_files.append(gf)
            genomic_files.append(gf)

        t = self._create_task('t1')
        db.session.add(t)
        db.session.add(study)
        db.session.commit()

    def _make_task_genomic_file(self, mock, **kwargs):
        """
        Create a new task_genomic_file with given is_input flag
        """
        # Create entities
        self._create_entities()

        t = kwargs.get('task_id')
        gf = kwargs.get('genomic_file_id')
        is_input = kwargs.get('is_input', True)

        if not (t and gf):
            t = Task.query.first().kf_id
            gf = GenomicFile.query.first().kf_id

        body = {
            'task_id': t,
            'genomic_file_id': gf,
            'is_input': is_input,
        }

        response = self.client.post(url_for(TASK_GF_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response
