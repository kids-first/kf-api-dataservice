import json
from flask import url_for
from urllib.parse import urlparse

from dataservice.extensions import db
from dataservice.api.common import id_service
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

DIAGNOSES_URL = 'api.diagnoses'
DIAGNOSES_LIST_URL = 'api.diagnoses_list'


class DiagnosisTest(FlaskTestCase):
    """
    Test diagnosis api
    """

    def test_post(self):
        """
        Test create a new diagnosis
        """
        # Create study
        study = Study(external_id='phs001')

        # Create a participant
        p = Participant(external_id='Test subject 0', is_proband=True,
                        study=study)
        db.session.add(p)
        db.session.commit()

        # Create diagnosis data
        kwargs = {
            'external_id': 'd1',
            'diagnosis': 'flu',
            'age_at_event_days': 365,
            'diagnosis_category': 'cancer',
            'tumor_location': 'Brain',
            'participant_id': p.kf_id
        }
        # Send get request
        response = self.client.post(url_for(DIAGNOSES_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        diagnosis = response['results']
        self.assertEqual(kwargs['external_id'], diagnosis['external_id'])
        self.assertEqual(kwargs['diagnosis'], diagnosis['diagnosis'])
        self.assertEqual(kwargs['age_at_event_days'],
                         diagnosis['age_at_event_days'])
        self.assertEqual(kwargs['diagnosis_category'],
                         diagnosis['diagnosis_category'])
        self.assertEqual(kwargs['tumor_location'], diagnosis['tumor_location'])

    def test_post_missing_req_params(self):
        """
        Test create diagnosis that is missing required parameters in body
        """
        # Create diagnosis data
        kwargs = {
            'external_id': 'd1',
            'diagnosis': 'flu',
            'age_at_event_days': 365,
            'diagnosis_category': 'cancer',
            'tumor_location': 'Brain'
            # missing required param participant_id
        }
        # Send post request
        response = self.client.post(url_for(DIAGNOSES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(kwargs))

        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not create diagnosis'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Diagnosis.query.first()
        self.assertIs(d, None)

    def test_post_invalid_age(self):
        """
        Test create diagnosis with bad input data

        Participant with participant_id does not exist in db
        """
        # Create diagnosis data
        kwargs = {
            'external_id': 'd1',
            'diagnosis': 'flu',
            'diagnosis_category': 'cancer',
            'tumor_location': 'Brain',
            # should be a positive integer
            'age_at_event_days': -5,
        }
        # Send post request
        response = self.client.post(url_for(DIAGNOSES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(kwargs))

        # Check status code
        self.assertEqual(response.status_code, 400)

        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not create diagnosis'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Diagnosis.query.first()
        self.assertIs(d, None)

    def test_post_bad_input(self):
        """
        Test create diagnosis with bad input data

        Participant with participant_id does not exist in db
        """
        # Create diagnosis data
        kwargs = {
            'external_id': 'd1',
            'diagnosis': 'flu',
            'age_at_event_days': 365,
            'diagnosis_category': 'cancer',
            'tumor_location': 'Brain',
            # kf_id does not exist
            'participant_id': id_service.kf_id_generator('PT')()
        }
        # Send post request
        response = self.client.post(url_for(DIAGNOSES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(kwargs))

        # Check status code
        self.assertEqual(response.status_code, 400)

        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = '"{}" does not exist'.format(kwargs['participant_id'])
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Diagnosis.query.first()
        self.assertIs(d, None)

    def test_post_multiple(self):
        # Create a diagnosis with participant
        d1 = self._create_save_to_db()
        # Create another diagnosis for the same participant
        d2 = {
            'external_id': 'd2',
            'diagnosis': 'cold',
            'diagnosis_category': 'cancer',
            'tumor_location': 'Brain',
            'participant_id': d1['participant_id']
        }
        # Send post request
        response = self.client.post(url_for(DIAGNOSES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(d2))
        # Check status code
        self.assertEqual(response.status_code, 201)
        # Check database
        c = Diagnosis.query.count()
        self.assertEqual(c, 2)
        pd = Participant.query.all()[0].diagnoses
        self.assertEqual(len(pd), 2)

    def test_get(self):
        # Create and save diagnosis to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(DIAGNOSES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        diagnosis = response['results']
        participant_link = response['_links']['participant']
        participant_id = urlparse(participant_link).path.split('/')[-1]
        self.assertEqual(diagnosis['kf_id'], kwargs['kf_id'])
        self.assertEqual(participant_id,
                         kwargs['participant_id'])
        self.assertEqual(diagnosis['external_id'], kwargs['external_id'])
        self.assertEqual(diagnosis['diagnosis'], kwargs['diagnosis'])
        self.assertEqual(kwargs['diagnosis_category'],
                         diagnosis['diagnosis_category'])
        self.assertEqual(kwargs['tumor_location'], diagnosis['tumor_location'])
        self.assertEqual(diagnosis['age_at_event_days'],
                         kwargs['age_at_event_days'])
        self.assertEqual(participant_id, kwargs['participant_id'])

    def test_get_not_found(self):
        """
        Test get diagnosis that does not exist
        """
        # Create diagnosis
        kf_id = 'non_existent'
        response = self.client.get(url_for(DIAGNOSES_URL, kf_id=kf_id),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 404)
        response = json.loads(response.data.decode("utf-8"))
        message = "could not find diagnosis `{}`".format(kf_id)
        self.assertIn(message, response['_status']['message'])

    def test_get_all(self):
        """
        Test retrieving all diagnoses
        """
        kwargs = self._create_save_to_db()

        response = self.client.get(url_for(DIAGNOSES_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

    def test_put(self):
        """
        Test update existing diagnosis
        """
        kwargs = self._create_save_to_db()

        # Send put request
        body = {
            'diagnosis': 'hangry',
            'diagnosis_category': 'birth defect',
            'participant_id': kwargs['participant_id']
        }
        response = self.client.put(url_for(DIAGNOSES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check field values got updated
        response = json.loads(response.data.decode('utf-8'))
        diagnosis = response['results']
        self.assertEqual(kwargs['kf_id'], diagnosis['kf_id'])
        # Fields that should be None since they were not in put request body
        self.assertIs(None, diagnosis['external_id'])
        self.assertIs(None, diagnosis['age_at_event_days'])
        self.assertIs(None, diagnosis['tumor_location'])
        # Fields that should be updated w values
        self.assertEqual(body['diagnosis'], diagnosis['diagnosis'])
        self.assertEqual(body['diagnosis_category'],
                         diagnosis['diagnosis_category'])

    def test_put_not_found(self):
        """
        Test update non-existent diagnosis
        """
        # Send put request
        kf_id = 'non-existent'
        body = {}
        response = self.client.put(url_for(DIAGNOSES_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 404)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not find diagnosis'
        self.assertIn(message, response['_status']['message'])
        # Check database
        c = Diagnosis.query.filter_by(kf_id=kf_id).count()
        self.assertEqual(c, 0)

    def test_put_bad_input(self):
        """
        Test update existing diagnosis with bad input

        Participant with participant_id does not exist
        """
        # Create and save diagnosis to db
        kwargs = self._create_save_to_db()

        # Send put request
        body = {
            'participant_id': 'AAAA1111'
        }
        response = self.client.put(url_for(DIAGNOSES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'participant "AAAA1111" does not exist'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Diagnosis.query.first()
        self.assertEqual(d.diagnosis, kwargs.get('diagnosis'))
        self.assertEqual(d.age_at_event_days, kwargs.get('age_at_event_days'))

    def test_put_missing_req_params(self):
        """
        Test create diagnosis that is missing required parameters in body
        """
        # Create and save diagnosis to db
        kwargs = self._create_save_to_db()
        # Create diagnosis data
        body = {
            'diagnosis': 'hangry and flu'
        }
        # Send put request
        response = self.client.put(url_for(DIAGNOSES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not update diagnosis'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Diagnosis.query.first()
        self.assertEqual(d.diagnosis, kwargs['diagnosis'])

    def test_delete(self):
        """
        Test delete an existing diagnosis
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(DIAGNOSES_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Diagnosis.query.first()
        self.assertIs(d, None)

    def test_delete_not_found(self):
        """
        Test delete diagnosis that does not exist
        """
        kf_id = 'non-existent'
        # Send get request
        response = self.client.delete(url_for(DIAGNOSES_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 404)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Diagnosis.query.first()
        self.assertIs(d, None)

    def _create_save_to_db(self):
        """
        Create and save diagnosis

        Requires creating a participant
        Create a diagnosis and add it to participant as kwarg
        Save participant
        """
        # Create study
        study = Study(external_id='phs001')

        # Create diagnosis
        kwargs = {
            'external_id': 'd1',
            'diagnosis': 'flu',
            'diagnosis_category': 'cancer',
            'tumor_location': 'Brain',
            'age_at_event_days': 365
        }
        d = Diagnosis(**kwargs)

        # Create and save participant with diagnosis
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, diagnoses=[d],
                        is_proband=True, study=study)
        db.session.add(p)
        db.session.commit()

        kwargs['participant_id'] = p.kf_id
        kwargs['kf_id'] = d.kf_id

        return kwargs
