import json
from flask import url_for
from urllib.parse import urlparse

from dataservice.extensions import db
from dataservice.api.common import id_service
from dataservice.api.outcome.models import Outcome
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

OUTCOMES_URL = 'api.outcomes'
OUTCOMES_LIST_URL = 'api.outcomes_list'


class OutcomeTest(FlaskTestCase):
    """
    Test outcome api
    """

    def test_post(self):
        """
        Test create a new outcome
        """
        # Create study
        study = Study(external_id='phs001')

        # Create a participant
        p = Participant(external_id='Test subject 0', is_proband=True,
                        study=study)
        db.session.add(p)
        db.session.commit()

        # Create outcome data
        kwargs = {
            'external_id': 'test_0',
            'vital_status': 'Alive',
            'disease_related': "Not Applicable",
            'age_at_event_days': 365,
            'participant_id': p.kf_id
        }
        # Send get request
        response = self.client.post(url_for(OUTCOMES_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        outcome = response['results']
        self.assertEqual(kwargs['age_at_event_days'],
                         outcome['age_at_event_days'])
        self.assertEqual(kwargs['vital_status'],
                         outcome['vital_status'])
        self.assertEqual(kwargs['disease_related'], outcome['disease_related'])

    def test_post_multiple(self):
        # Create a outcome with participant
        oc1 = self._create_save_to_db()
        # Create another outcome for the same participant
        oc2 = {
            'external_id': 'test_1',
            'vital_status': 'Dead',
            'disease_related': 'Yes',
            'age_at_event_days': 369,
            'participant_id': oc1['participant_id']
        }
        # Send post request
        response = self.client.post(url_for(OUTCOMES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(oc2))
        # Check status code
        self.assertEqual(response.status_code, 201)
        # Check database
        oc = Outcome.query.count()
        self.assertEqual(oc, 2)
        po = Participant.query.all()[0].outcomes
        self.assertEqual(len(po), 2)

    def test_get(self):
        # Create and save outcome to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(OUTCOMES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        outcome = response['results']
        participant_link = response['_links']['participant']
        participant_id = urlparse(participant_link).path.split('/')[-1]
        self.assertEqual(outcome['kf_id'], kwargs['kf_id'])
        self.assertEqual(participant_id,
                         kwargs['participant_id'])
        self.assertEqual(kwargs['vital_status'],
                         outcome['vital_status'])
        self.assertEqual(kwargs['disease_related'], outcome['disease_related'])
        self.assertEqual(outcome['age_at_event_days'],
                         kwargs['age_at_event_days'])
        self.assertEqual(participant_id, kwargs['participant_id'])

    def test_get_all(self):
        """
        Test retrieving all outcomes
        """
        kwargs = self._create_save_to_db()

        response = self.client.get(url_for(OUTCOMES_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

    def test_patch(self):
        """
        Test update existing outcome
        """
        kwargs = self._create_save_to_db()

        # Send patch request
        body = {
            'vital_status': 'Dead',
            'participant_id': kwargs['participant_id']
        }
        response = self.client.patch(url_for(OUTCOMES_URL,
                                             kf_id=kwargs['kf_id']),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check field values got updated
        response = json.loads(response.data.decode('utf-8'))
        outcome = response['results']
        self.assertEqual(kwargs['kf_id'], outcome['kf_id'])

        # Fields that should be updated w values
        self.assertEqual(body['vital_status'],
                         outcome['vital_status'])

    def test_delete(self):
        """
        Test delete an existing outcome
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(OUTCOMES_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        o = Outcome.query.first()
        self.assertIs(o, None)

    def _create_save_to_db(self):
        """
        Create and save outcome

        Requires creating a participant
        Create a outcome and add it to participant as kwarg
        Save participant
        """
        # Create study
        study = Study(external_id='phs001')

        # Create outcome
        kwargs = {
            'external_id': 'test_0',
            'vital_status': 'Alive',
            'disease_related': 'No',
            'age_at_event_days': 365
        }
        oc = Outcome(**kwargs)

        # Create and save participant with outcome
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, outcomes=[oc],
                        is_proband=True, study=study)
        db.session.add(p)
        db.session.commit()

        kwargs['participant_id'] = p.kf_id
        kwargs['kf_id'] = oc.kf_id

        return kwargs
