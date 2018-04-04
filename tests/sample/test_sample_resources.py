import json
from urllib.parse import urlparse
from datetime import datetime
from dateutil import parser, tz

from flask import url_for

from dataservice.extensions import db
from dataservice.api.common import id_service
from dataservice.api.sample.models import Sample
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

SAMPLES_URL = 'api.samples'
SAMPLES_LIST_URL = 'api.samples_list'


class SampleTest(FlaskTestCase):
    """
    Test sample api
    """

    def test_post(self):
        """
        Test create a new sample
        """
        kwargs = self._create_save_to_db()
        # Create sample data
        kwargs = {
            'external_id': 's1',
            'tissue_type': 'Normal',
            'composition': 'composition1',
            'anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'tumor_descriptor': 'Metastatic',
            'participant_id': kwargs.get('participant_id')
        }

        # Send post request
        response = self.client.post(url_for(SAMPLES_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sample = response['results']
        for k, v in kwargs.items():
            if k is not 'participant_id':
                self.assertEqual(sample.get(k), v)
        self.assertEqual(2, Sample.query.count())

    def test_post_missing_req_params(self):
        """
        Test create sample that is missing required parameters in body
        """
        # Create sample data
        kwargs = {
            'external_id': 's1'
            # missing required param participant_id
        }
        # Send post request
        response = self.client.post(url_for(SAMPLES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(kwargs))

        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not create sample'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Sample.query.first()
        self.assertIs(d, None)

    def test_post_invalid_age(self):
        """
        Test create sample with bad input data

        Invalid age
        """
        # Create sample data
        kwargs = {
            'external_id': 's1',
            # should be a positive integer
            'age_at_event_days': -5,
        }
        # Send post request
        response = self.client.post(url_for(SAMPLES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(kwargs))

        # Check status code
        self.assertEqual(response.status_code, 400)

        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not create sample'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Sample.query.first()
        self.assertIs(d, None)

    def test_post_bad_input(self):
        """
        Test create sample with bad input data

        Participant with participant_id does not exist in db
        """
        # Create sample data
        kwargs = {
            'external_id': 's1',
            'tissue_type': 'Normal',
            'composition': 'composition1',
            'anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'tumor_descriptor': 'Metastatic',
            # kf_id does not exist
            'participant_id': id_service.kf_id_generator('PT')()
        }
        # Send post request
        response = self.client.post(url_for(SAMPLES_LIST_URL),
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
        d = Sample.query.first()
        self.assertIs(d, None)

    def test_post_multiple(self):
        # Create a sample with participant
        s1 = self._create_save_to_db()
        # Create another sample for the same participant
        s2 = {
            'external_id': 's2',
            'tissue_type': 'abnormal',
            'participant_id': s1['participant_id']
        }
        # Send post request
        response = self.client.post(url_for(SAMPLES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(s2))
        # Check status code
        self.assertEqual(response.status_code, 201)
        # Check database
        c = Sample.query.count()
        self.assertEqual(c, 2)
        samples = Participant.query.all()[0].samples
        self.assertEqual(len(samples), 2)

    def test_get(self):
        # Create and save sample to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(SAMPLES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sample = response['results']
        participant_link = response['_links']['participant']
        participant_id = urlparse(participant_link).path.split('/')[-1]
        for k, v in kwargs.items():
            if k is not 'participant_id':
                self.assertEqual(sample.get(k), v)
        self.assertEqual(participant_id,
                         kwargs['participant_id'])

    def test_get_all(self):
        """
        Test retrieving all samples
        """
        kwargs = self._create_save_to_db()

        response = self.client.get(url_for(SAMPLES_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

    def test_patch(self):
        """
        Test updating an existing sample
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')

        # Update existing sample
        body = {
            'tissue_type': 'saliva',
            'participant_id': kwargs['participant_id']
        }
        response = self.client.patch(url_for(SAMPLES_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('sample', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        sample = resp['results']
        sa = Sample.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(sa, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(sample.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(sa, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(str(parser.parse(sample[k])), str(d))
            else:
                self.assertEqual(sample[k], val)

        self.assertEqual(1, Sample.query.count())

    def test_patch_bad_input(self):
        """
        Test updating an existing participant with invalid input
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')
        body = {
            'participant_id': 'AAAA1111'
        }
        response = self.client.patch(url_for(SAMPLES_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'participant "AAAA1111" does not exist'
        self.assertIn(message, response['_status']['message'])
        # Check that properties are unchanged
        sa = Sample.query.first()
        for k, v in kwargs.items():
            if k == 'participant_id':
                continue
            self.assertEqual(v, getattr(sa, k))

    def test_patch_missing_req_params(self):
        """
        Test create sample that is missing required parameters in body
        """
        # Create and save diagnosis to db
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')
        # Create diagnosis data
        body = {
            'tissue_type': 'blood'
        }
        # Send put request
        response = self.client.patch(url_for(SAMPLES_URL,
                                             kf_id=kwargs['kf_id']),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check field values
        sa = Sample.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(sa, k))

    def test_delete(self):
        """
        Test delete an existing sample
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(SAMPLES_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Sample.query.first()
        self.assertIs(d, None)

    def test_delete_not_found(self):
        """
        Test delete sample that does not exist
        """
        kf_id = 'non-existent'
        # Send get request
        response = self.client.delete(url_for(SAMPLES_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 404)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Sample.query.first()
        self.assertIs(d, None)

    def _create_save_to_db(self):
        """
        Create and save sample

        Requires creating a participant
        Create a sample and add it to participant as kwarg
        Save participant
        """
        study = Study(external_id='phs001')
        db.session.add(study)
        db.session.commit()

        # Create sample
        kwargs = {
            'external_id': 's1',
            'tissue_type': 'Normal',
            'composition': 'composition1',
            'anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'tumor_descriptor': 'Metastatic'
        }
        s = Sample(**kwargs)

        # Create and save participant with sample
        p = Participant(external_id='Test subject 0', samples=[s],
                        is_proband=True, study_id=study.kf_id)
        db.session.add(p)
        db.session.commit()

        kwargs['participant_id'] = p.kf_id
        kwargs['kf_id'] = s.kf_id

        return kwargs
