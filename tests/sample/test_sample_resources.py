import json
from flask import url_for
from urllib.parse import urlparse

from dataservice.extensions import db
from dataservice.api.common import id_service
from dataservice.api.sample.models import Sample
from dataservice.api.participant.models import Participant
from tests.utils import FlaskTestCase

SAMPLES_URL = 'api.samples'


class SampleTest(FlaskTestCase):
    """
    Test sample api
    """

    def test_post(self):
        """
        Test create a new sample
        """
        # Create a participant
        p = Participant(external_id='Test subject 0')
        db.session.add(p)
        db.session.commit()

        # Create sample data
        kwargs = {
            'external_id': 's1',
            'tissue_type': 'Normal',
            'composition': 'composition1',
            'anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'tumor_descriptor': 'Metastatic',
            'participant_id': p.kf_id
        }
        # Send post request
        response = self.client.post(url_for(SAMPLES_URL),
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
        response = self.client.post(url_for(SAMPLES_URL),
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
        response = self.client.post(url_for(SAMPLES_URL),
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
            'participant_id': id_service.kf_id_generator()
        }
        # Send post request
        response = self.client.post(url_for(SAMPLES_URL),
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
        response = self.client.post(url_for(SAMPLES_URL),
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

    def test_get_not_found(self):
        """
        Test get sample that does not exist
        """
        # Create sample
        kf_id = 'non_existent'
        response = self.client.get(url_for(SAMPLES_URL, kf_id=kf_id),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 404)
        response = json.loads(response.data.decode("utf-8"))
        message = "could not find sample `{}`".format(kf_id)
        self.assertIn(message, response['_status']['message'])

    def test_get_all(self):
        """
        Test retrieving all samples
        """
        kwargs = self._create_save_to_db()

        response = self.client.get(url_for(SAMPLES_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

    def test_put(self):
        """
        Test update existing sample
        """
        kwargs = self._create_save_to_db()

        # Send put request
        body = {
            'tissue_type': 'abnormal',
            'participant_id': kwargs['participant_id']
        }
        response = self.client.put(url_for(SAMPLES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check field values got updated
        response = json.loads(response.data.decode('utf-8'))
        sample = response['results']
        self.assertEqual(kwargs['kf_id'], sample['kf_id'])
        # Fields that should be None since they were not in put request body
        self.assertIs(None, sample['external_id'])
        self.assertIs(None, sample['composition'])
        self.assertIs(None, sample['anatomical_site'])
        self.assertIs(None, sample['tumor_descriptor'])
        self.assertEqual([], sample['aliquots'])
        # Fields that should be updated w values
        self.assertEqual(body['tissue_type'], sample['tissue_type'])

    def test_put_not_found(self):
        """
        Test update non-existent sample
        """
        # Send put request
        kf_id = 'non-existent'
        body = {}
        response = self.client.put(url_for(SAMPLES_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 404)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not find sample'
        self.assertIn(message, response['_status']['message'])
        # Check database
        c = Sample.query.filter_by(kf_id=kf_id).count()
        self.assertEqual(c, 0)

    def test_put_bad_input(self):
        """
        Test update existing sample with bad input

        Participant with participant_id does not exist
        """
        # Create and save sample to db
        kwargs = self._create_save_to_db()

        # Send put request
        body = {
            'participant_id': 'AAAA1111'
        }
        response = self.client.put(url_for(SAMPLES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'Cannot update sample without an existing'
        message = 'participant "AAAA1111" does not exist'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Sample.query.first()
        self.assertEqual(d.tissue_type, kwargs.get('tissue_type'))
        self.assertEqual(d.age_at_event_days, kwargs.get('age_at_event_days'))

    def test_put_missing_req_params(self):
        """
        Test create sample that is missing required parameters in body
        """
        # Create and save sample to db
        kwargs = self._create_save_to_db()
        # Create sample data
        body = {
            'tissue_type': 'abnormal'
        }
        # Send put request
        response = self.client.put(url_for(SAMPLES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not update sample'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Sample.query.first()
        self.assertEqual(d.tissue_type, kwargs['tissue_type'])

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
        # Create sample
        kwargs = {
            'external_id': 's1',
            'tissue_type': 'Normal',
            'composition': 'composition1',
            'anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'tumor_descriptor': 'Metastatic',
        }
        d = Sample(**kwargs)

        # Create and save participant with sample
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, samples=[d])
        db.session.add(p)
        db.session.commit()

        kwargs['participant_id'] = p.kf_id
        kwargs['kf_id'] = d.kf_id

        return kwargs
