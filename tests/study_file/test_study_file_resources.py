import json

from flask import url_for

from dataservice.extensions import db
from dataservice.api.study_file.models import StudyFile
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

STUDY_FILE_URL = 'api.study_files'
STUDY_FILE_LIST_URL = 'api.study_files_list'


class StudyFileTest(FlaskTestCase):
    '''
    Test study_file api endopoints
    '''

    def test_post_study_file(self):
        '''
        Test creating a new study_file
        '''
        response = self._make_study_file(file_name='TEST')
        resp = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)

        self.assertIn('study_file', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])
        self.assertNotIn('_id', resp['results'])

        s = StudyFile.query.first()
        study_file = resp['results']
        self.assertEqual(1, StudyFile.query.count())
        self.assertEqual(s.kf_id, study_file['kf_id'])
        self.assertEqual(s.file_name, study_file['file_name'])

    def test_get_study_file(self):
        '''
        Test retrieving a study_file by id
        '''
        resp = self._make_study_file(file_name='TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(STUDY_FILE_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        study_file = resp['results']
        self.assertEqual(kf_id, study_file['kf_id'])

    def test_patch_study_file(self):
        '''
        Test updating an existing study_file
        '''
        response = self._make_study_file(file_name='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        study_file = resp['results']
        kf_id = study_file.get('kf_id')
        file_name = study_file.get('file_name')

        # Update the study_file via http api
        body = {
            'file_name': 'investigator.txt'
        }
        response = self.client.patch(url_for(STUDY_FILE_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(StudyFile.query.get(kf_id).file_name,
                         body['file_name'])

        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('study_file', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        study_file = resp['results']
        self.assertEqual(study_file['kf_id'], kf_id)
        self.assertEqual(study_file['file_name'], body['file_name'])

    def test_patch_study_file_no_required_field(self):
        '''
        Test that we may update the study_file without a required field
        '''
        response = self._make_study_file(file_name='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        study_file = resp['results']
        kf_id = study_file.get('kf_id')
        file_name = study_file.get('file_name')

        # Update the study_file via http api
        body = {
            'file_name': 'TEST-2'
        }
        response = self.client.patch(url_for(STUDY_FILE_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        self.assertEqual(response.status_code, 200)


        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('study_file', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        study_file = resp['results']
        self.assertEqual(study_file['kf_id'], kf_id)
        self.assertEqual(study_file['file_name'], body['file_name'])
        
    def test_delete_study_file(self):
        '''
        Test deleting a study_file by id
        '''
        resp = self._make_study_file(file_name='TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(STUDY_FILE_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url_for(STUDY_FILE_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def _make_study_file(self, file_name='TEST'):
        '''
        Convenience method to create a study_file with a given source name
        '''
        # Create study
        study = Study(external_id='phs001')
        db.session.add(study)
        db.session.commit()
        body = {
            'file_name': file_name,
            'study_id': study.kf_id
        }

        response = self.client.post(url_for(STUDY_FILE_LIST_URL),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        return response
