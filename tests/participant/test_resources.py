import json
from flask import url_for

from dataservice.api.participant.models import Participant
from tests.utils import FlaskTestCase

PARTICIPANTS_PREFIX = 'api.participants'
PARTICIPANT_URL = '{}_{}'.format(PARTICIPANTS_PREFIX, 'participant')
PARTICIPANT_LIST_URL = '{}_{}'.format(PARTICIPANTS_PREFIX, 'participant_list')


class ParticipantTest(FlaskTestCase):
    """
    Test participant api
    """

    def test_post_participant(self):
        """
        Test creating a new participant
        """
        response = self._make_participant(external_id="TEST")
        self.assertEqual(response.status_code, 201)

        resp = json.loads(response.data.decode("utf-8"))
        self._test_response_content(resp, 201)

        self.assertEqual('participant created', resp['_status']['message'])

        p = Participant.query.first()
        participant = resp['results'][0]
        self.assertEqual(p.kf_id, participant['kf_id'])
        self.assertEqual(p.external_id, participant['external_id'])

    def test_get_not_found(self):
        """
        Test get participant that does not exist
        """
        kf_id = 'non_existent'
        response = self.client.get(url_for(PARTICIPANT_URL, kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self._test_response_content(resp, 404)
        message = "participant with kf_id '{}' not found".format(kf_id)
        self.assertIn(message, resp['_status']['message'])

    def test_get_participant(self):
        """
        Test retrieving a participant by id
        """
        resp = self._make_participant("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results'][0]['kf_id']

        response = self.client.get(url_for(PARTICIPANT_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self._test_response_content(resp, 200)

        participant = resp['results'][0]

        self.assertEqual(kf_id, participant['kf_id'])

    def test_get_all_participants(self):
        """
        Test retrieving all participants
        """
        self._make_participant(external_id="MyTestParticipant1")

        response = self.client.get(url_for(PARTICIPANT_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_put_participant(self):
        """
        Test updating an existing participant
        """
        response = self._make_participant(external_id="TEST")
        resp = json.loads(response.data.decode("utf-8"))
        participant = resp['results'][0]
        kf_id = participant.get('kf_id')
        external_id = participant.get('external_id')

        body = {
            'external_id': 'Updated-{}'.format(external_id)
        }
        response = self.client.put(url_for(PARTICIPANT_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers(),
                                   data=json.dumps(body))
        self.assertEqual(response.status_code, 201)

        resp = json.loads(response.data.decode("utf-8"))
        self._test_response_content(resp, 201)
        self.assertEqual('participant updated', resp['_status']['message'])

        p = Participant.query.first()
        participant = resp['results'][0]
        self.assertEqual(p.kf_id, participant['kf_id'])
        self.assertEqual(p.external_id, participant['external_id'])

    def test_delete_participant(self):
        """
        Test deleting a participant by id
        """
        resp = self._make_participant("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results'][0]['kf_id']

        response = self.client.delete(url_for(PARTICIPANT_URL,
                                              kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url_for(PARTICIPANT_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 404)

    def _make_participant(self, external_id="TEST-0001"):
        """
        Convenience method to create a participant with a given source name
        """
        body = {
            'external_id': external_id
        }
        response = self.client.post(url_for(PARTICIPANT_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))

        return response

    def _test_response_content(self, resp, status_code):
        """
        Test that response body has expected fields
        """
        self.assertIn('results', resp)
        self.assertIn('_status', resp)
        self.assertIn('message', resp['_status'])
        self.assertEqual(resp['_status']['code'], status_code)
