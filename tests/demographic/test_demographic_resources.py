import json
from flask import url_for
from datetime import datetime
from dateutil import parser, tz
from urllib.parse import urlparse

from dataservice.extensions import db
from dataservice.api.common import id_service
from dataservice.api.demographic.models import Demographic
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

DEMOGRAPHICS_URL = 'api.demographics'
DEMOGRAPHICS_LIST_URL = 'api.demographics_list'


class DemographicTest(FlaskTestCase):
    """
    Test demographic api
    """

    def test_post(self):
        """
        Test create a new demographic
        """
        study = Study(external_id='phs001')
        db.session.add(study)
        db.session.commit()

        # Create a demographic
        p = Participant(external_id='Test subject 0', is_proband=True,
                        study_id=study.kf_id)
        db.session.add(p)
        db.session.commit()

        # Create demographic data
        kwargs = {
            'external_id': 'd1',
            'race': 'asian',
            'ethnicity': 'not hispanic or latino',
            'gender': 'female',
            'participant_id': p.kf_id
        }
        # Send get request
        response = self.client.post(url_for(DEMOGRAPHICS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        demographic = response['results']
        dm = Demographic.query.get(demographic.get('kf_id'))
        for k, v in kwargs.items():
            if k == 'participant_id':
                continue
            self.assertEqual(demographic[k], getattr(dm, k))

    def test_post_missing_req_params(self):
        """
        Test create demographic that is missing required parameters in body
        """
        # Create demographic data
        kwargs = {
            'external_id': 'd1',
            'race': 'asian',
            'ethnicity': 'not hispanic or latino',
            'gender': 'female'
        }
        # Send post request
        response = self.client.post(url_for(DEMOGRAPHICS_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(kwargs))

        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not create demographic'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        d = Demographic.query.first()
        self.assertIs(d, None)

    def test_post_bad_input(self):
        """
        Test create demographic with bad input data

        Participant with participant_id does not exist in db
        """
        # Create demographic data
        kwargs = {
            'external_id': 'd1',
            'race': 'asian',
            'ethnicity': 'not hispanic or latino',
            'gender': 'female',
            'participant_id': id_service.kf_id_generator('PT')()
        }
        # Send post request
        response = self.client.post(url_for(DEMOGRAPHICS_LIST_URL),
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
        d = Demographic.query.first()
        self.assertIs(d, None)

    def test_post_multiple(self):
        # Create a demographic with participant
        d1 = self._create_save_to_db()
        # Create another demographic for the same participant
        d2 = {
            'external_id': 'd1',
            'race': 'asian',
            'ethnicity': 'not hispanic or latino',
            'gender': 'female',
            'participant_id': d1['participant_id']
        }
        # Send post request
        response = self.client.post(url_for(DEMOGRAPHICS_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(d2))
        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'participant "{}" may only have one demographic'
        message = message.format(d1['participant_id'])
        self.assertIn(message, response['_status']['message'])

        # Check database
        c = Demographic.query.count()
        self.assertEqual(c, 1)

    def test_get(self):
        # Create and save demographic to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(DEMOGRAPHICS_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        demographic = response['results']
        participant_link = response['_links']['participant']
        participant_id = urlparse(participant_link).path.split('/')[-1]
        self.assertEqual(demographic['kf_id'], kwargs['kf_id'])
        self.assertEqual(participant_id,
                         kwargs['participant_id'])
        self.assertEqual(demographic['external_id'], kwargs['external_id'])
        self.assertEqual(demographic['race'], kwargs['race'])
        self.assertEqual(demographic['gender'], kwargs['gender'])
        self.assertEqual(demographic['ethnicity'], kwargs['ethnicity'])

    def test_get_not_found(self):
        """
        Test get demographic that does not exist
        """
        # Create demographic
        kf_id = 'non_existent'
        response = self.client.get(url_for(DEMOGRAPHICS_URL, kf_id=kf_id),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 404)
        response = json.loads(response.data.decode("utf-8"))
        message = "could not find demographic `{}`".format(kf_id)
        self.assertIn(message, response['_status']['message'])

    def test_get_all(self):
        """
        Test retrieving all demographics
        """
        kwargs = self._create_save_to_db()

        response = self.client.get(url_for(DEMOGRAPHICS_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

    def test_patch(self):
        """
        Test update existing demographic
        """
        # Send patch request
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')
        body = {
            'race': 'black or african',
            'gender': 'male',
            'participant_id': kwargs['participant_id']
        }
        response = self.client.patch(url_for(DEMOGRAPHICS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self._test_response_content(resp, 200)
        self.assertIn('demographic', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        demographic = resp['results']
        dm = Demographic.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(dm, k))

        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(demographic.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(dm, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(str(parser.parse(demographic[k])), str(d))
            else:
                self.assertEqual(demographic[k], val)

        self.assertEqual(1, Demographic.query.count())

    def test_patch_bad_input(self):
        """
        Test updating an existing participant with invalid input
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')
        body = {
            'race': 'black or african',
            'gender': 'male',
            'participant_id': 'AAAA1111'
        }
        response = self.client.patch(url_for(DEMOGRAPHICS_URL,
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
        d = Demographic.query.first()
        for k, v in kwargs.items():
            if k == 'participant_id':
                continue
            self.assertEqual(v, getattr(d, k))

    def test_delete(self):
        """
        Test delete an existing demographic
        """
        kwargs = self._create_save_to_db()

        # Send get request
        response = self.client.delete(url_for(DEMOGRAPHICS_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Demographic.query.first()
        self.assertIs(d, None)

    def test_delete_not_found(self):
        """
        Test delete demographic that does not exist
        """
        kf_id = 'non-existent'
        # Send get request
        response = self.client.delete(url_for(DEMOGRAPHICS_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 404)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Demographic.query.first()
        self.assertIs(d, None)

    def _create_save_to_db(self):
        """
        Create and save demographic

        Requires creating a participant
        Create a demographic and add it to participant as kwarg
        Save participant
        """
        study = Study(external_id='phs001')
        db.session.add(study)
        db.session.commit()

        # Create demographic
        kwargs = {
            'external_id': 'd1',
            'race': 'asian',
            'ethnicity': 'not hispanic or latino',
            'gender': 'female'
        }
        d = Demographic(**kwargs)

        # Create and save participant with demographic
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, demographic=d,
                        is_proband=True, study_id=study.kf_id)
        db.session.add(p)
        db.session.commit()

        kwargs['participant_id'] = p.kf_id
        kwargs['kf_id'] = d.kf_id

        return kwargs

    def _test_response_content(self, resp, status_code):
        """
        Test that response body has expected fields
        """
        self.assertIn('results', resp)
        self.assertIn('_status', resp)
        self.assertIn('message', resp['_status'])
        self.assertEqual(resp['_status']['code'], status_code)
