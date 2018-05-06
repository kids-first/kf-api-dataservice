import json
from datetime import datetime
from dateutil import parser, tz

from flask import url_for

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.family.models import Family
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

PARTICIPANT_URL = 'api.participants'
PARTICIPANT_LIST_URL = 'api.participants_list'


class ParticipantTest(FlaskTestCase):
    """
    Test participant api
    """

    def test_post_participant(self):
        """
        Test creating a new participant
        """
        response = self._make_participant(external_id="TEST")
        resp = json.loads(response.data.decode("utf-8"))

        self.assertEqual(response.status_code, 201)

        self.assertIn('participant', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])
        self.assertNotIn('_id', resp['results'])

        p = Participant.query.first()
        participant = resp['results']
        self.assertEqual(p.kf_id, participant['kf_id'])
        self.assertEqual(p.external_id, participant['external_id'])
        self.assertEqual(p.consent_type, participant['consent_type'])
        self.assertEqual(p.family_id, resp['_links']['family'][-11:])
        self.assertEqual(p.is_proband, participant['is_proband'])
        self.assertEqual(p.race, participant['race'])
        self.assertEqual(p.ethnicity, participant['ethnicity'])
        self.assertEqual(p.gender, participant['gender'])

    def test_post_with_kf_id(self):
        """
        Test creating a new participant with a predetermined kf_id
        """
        s = Study(external_id='phs001')
        db.session.add(s)
        db.session.commit()

        body = {
            'kf_id': 'PT_00000000',
            'external_id': 'test',
            'is_proband': True,
            'consent_type': 'GRU-IRB',
            'race': 'asian',
            'ethnicity': 'not hispanic',
            'gender': 'female',
            'study_id': s.kf_id
        }

        response = self.client.post(url_for(PARTICIPANT_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))

        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 201)

        self.assertEqual(resp['results']['kf_id'], 'PT_00000000')

        p = Participant.query.first()
        self.assertEqual(p.kf_id, resp['results']['kf_id'])
        self.assertEqual(p.kf_id, 'PT_00000000')

    def test_post_missing_req_params(self):
        """
        Test create participant that is missing required parameters in body
        """
        # Create participant data
        body = {
            'external_id': 'p1'
        }
        # Send post request
        response = self.client.post(url_for(PARTICIPANT_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))

        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not create participant'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        p = Participant.query.first()
        self.assertIs(p, None)

    def test_get_participant(self):
        """
        Test retrieving a participant by id
        """
        resp = self._make_participant("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(PARTICIPANT_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

        participant = resp['results']
        p = Participant.query.first()
        self.assertEqual(kf_id, participant['kf_id'])
        self.assertEqual(p.consent_type, participant['consent_type'])
        self.assertTrue(resp['_links']['family'].endswith(p.family_id))

    def test_get_participant_no_family(self):
        """
        Test that there is no family link if the participant doesnt have one
        """
        resp = self._make_participant(include_nullables=False)
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(PARTICIPANT_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

        self.assertTrue('family' in resp['_links'])
        self.assertIs(None, resp['_links']['family'])

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

    def test_patch_participant(self):
        """
        Test updating an existing participant
        """
        response = self._make_participant(external_id="TEST")
        resp = json.loads(response.data.decode("utf-8"))
        participant = resp['results']
        kf_id = participant.get('kf_id')
        # Update existing participant
        body = {
            'external_id': 'participant 0',
            'consent_type': 'something',
            'gender': 'updated_gender',
            'kf_id': kf_id
        }
        response = self.client.patch(url_for(PARTICIPANT_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('participant', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        p = Participant.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(p, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(participant.keys()) -
                          set(body.keys()) -
                          {'modified_at'})
        for k in unchanged_keys:
            val = getattr(p, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(str(parser.parse(participant[k])), str(d))
            else:
                self.assertEqual(participant[k], val)

        self.assertEqual(1, Participant.query.count())

    def test_patch_bad_input(self):
        """
        Test updating an existing participant with invalid input
        """
        response = self._make_participant(external_id="TEST")
        resp = json.loads(response.data.decode("utf-8"))
        participant = resp['results']
        kf_id = participant.get('kf_id')
        # Update existing participant
        body = {
            'external_id': 'participant 0',
            'is_proband': 'should be a boolean',
            'kf_id': kf_id
        }
        response = self.client.patch(url_for(PARTICIPANT_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 400)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check error message
        message = 'could not update participant'
        self.assertIn(message, response['_status']['message'])
        # Check field values
        p = Participant.query.first()
        for k, v in participant.items():
            val = getattr(p, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(str(parser.parse(v)), str(d))
            else:
                self.assertEqual(v, val)

    def test_delete_participant(self):
        """
        Test deleting a participant by id
        """
        resp = self._make_participant("TEST")
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results']['kf_id']

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

    def _make_participant(self, external_id="TEST-0001",
                          include_nullables=True):
        """
        Convenience method to create a participant with a given source name
        """
        # Make required entities first
        s = Study(external_id='phs001')
        fam = Family(external_id='family0')
        db.session.add_all([s, fam])
        db.session.commit()

        body = {
            'external_id': external_id,
            'is_proband': True,
            'consent_type': 'GRU-IRB',
            'race': 'asian',
            'ethnicity': 'not hispanic',
            'gender': 'female',
            'study_id': s.kf_id
        }
        if include_nullables:
            body.update({'family_id': fam.kf_id})

        response = self.client.post(url_for(PARTICIPANT_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response
