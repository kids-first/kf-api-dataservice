import json
from pprint import pprint
from flask import url_for
from urllib.parse import urlparse
from sqlalchemy import or_

from dataservice.extensions import db
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.family.models import Family
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

FAMILY_RELATIONSHIPS_URL = 'api.family_relationships'
FAMILY_RELATIONSHIPS_LIST_URL = 'api.family_relationships_list'


class FamilyRelationshipTest(FlaskTestCase):
    """
    Test family_relationship api
    """

    def test_post(self):
        """
        Test create a new family_relationship
        """
        p1, p2, p3, p4, s1, kwargs = self._create_save_to_db()

        # Create new family relationship
        results = Participant.query.filter(
            or_
            (Participant.external_id == 'Pebbles',
             Participant.external_id == 'Dino'))
        kwargs = {
            'participant1_id': results[0].kf_id,
            'participant2_id': results[1].kf_id,
            'participant1_to_participant2_relation': 'father'
        }
        # Send get request
        response = self.client.post(url_for(FAMILY_RELATIONSHIPS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        family_relationship = response['results']
        fr = FamilyRelationship.query.get(family_relationship.get('kf_id'))
        for k, v in kwargs.items():
            if k == 'participant1_id':
                self.assertEqual(v, kwargs.get('participant1_id'))
            elif k == 'participant2_id':
                self.assertEqual(v, kwargs.get('participant2_id'))
            else:
                self.assertEqual(family_relationship[k], getattr(fr, k))
        self.assertEqual(2, FamilyRelationship.query.count())

    def test_get(self):
        # Create and save family_relationship to db
        p1, p2, p3, p4, s1, kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(FAMILY_RELATIONSHIPS_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        family_relationship = response['results']
        participant_link = response['_links']['participant1']
        participant1_id = urlparse(participant_link).path.split('/')[-1]
        participant2_link = response['_links']['participant2']
        participant2_id = urlparse(participant2_link).path.split('/')[-1]
        for k, v in kwargs.items():
            if k == 'participant1_id':
                self.assertEqual(participant1_id,
                                 kwargs['participant1_id'])
            elif k == 'participant2_id':
                self.assertEqual(participant2_id,
                                 kwargs['participant2_id'])
            else:
                self.assertEqual(family_relationship[k],
                                 family_relationship[k])

    def test_get_all(self):
        """
        Test retrieving all family_relationships
        """
        self._create_save_to_db()
        self._create_save_to_db()

        response = self.client.get(url_for(FAMILY_RELATIONSHIPS_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 2)

    def test_patch(self):
        """
        Test updating an existing family_relationship
        """
        p1, p2, p3, p4, s1, kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')

        # Update existing family_relationship
        body = {
            'participant1_to_participant2_relation': 'mother'
        }
        response = self.client.patch(url_for(FAMILY_RELATIONSHIPS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('family_relationship', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        family_relationship = resp['results']
        fr = FamilyRelationship.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(fr, k))
        # Unchanged
        self.assertEqual(kwargs.get('participant2_to_participant1_relation'),
                         family_relationship.get(
                         'participant2_to_participant1_relation'))
        self.assertEqual(1, FamilyRelationship.query.count())

    def test_delete(self):
        """
        Test delete an existing family_relationship
        """
        p1, p2, p3, p4, s1, kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(FAMILY_RELATIONSHIPS_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        fr = FamilyRelationship.query.first()
        self.assertIs(fr, None)

    def test_special_filter_param(self):
        """
        Test special filter param participant_id

        /family-relationships?participant_id
        """
        # Add some family relationships
        p1, p2, p3, p4, s1, kwargs = self._create_save_to_db()
        r2 = FamilyRelationship(participant1=p1, participant2=p4,
                                participant1_to_participant2_relation='father')
        r3 = FamilyRelationship(participant1=p2, participant2=p3,
                                participant1_to_participant2_relation='mother')
        r4 = FamilyRelationship(participant1=p2, participant2=p4,
                                participant1_to_participant2_relation='mother')
        db.session.add_all([r2, r3, r4])
        db.session.commit()

        # Case 1 - Participant with no family defined
        url = (url_for(FAMILY_RELATIONSHIPS_LIST_URL) +
               '?participant_id={}'.format(p3.kf_id))
        response = self.client.get(url, headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        # Only immediate family relationships returned
        self.assertEqual(len(content), 2)

        # Test with additional filter parameters
        url = (url_for(FAMILY_RELATIONSHIPS_LIST_URL) +
               '?participant_id={}'
               '&study_id={}&participant1_to_participant2_relation={}'
               .format(p3.kf_id, s1.kf_id, 'father'))
        response = self.client.get(url, headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

        # Case 2 - Participant with a family defined
        f0 = Family(external_id='phs001-family')
        f0.participants.extend([p1, p2, p3, p4])
        db.session.add(f0)
        db.session.commit()

        url = (url_for(FAMILY_RELATIONSHIPS_LIST_URL) +
               '?participant_id={}'.format(p3.kf_id))
        response = self.client.get(url, headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        # All family relationships returned
        self.assertEqual(len(content), 4)

        # Add another study with a family and relationships
        s2 = Study(external_id='phs002')
        f2 = Family(external_id='phs002-family')
        p_1 = Participant(external_id='Fred_1', is_proband=False)
        p_2 = Participant(external_id='Wilma_1',  is_proband=False)
        p_3 = Participant(external_id='Pebbles_1', is_proband=True)

        r_1 = FamilyRelationship(
            participant1=p_1, participant2=p_3,
            participant1_to_participant2_relation='father')
        r_2 = FamilyRelationship(
            participant1=p_2, participant2=p_3,
            participant1_to_participant2_relation='mother')

        s2.participants.extend([p_1, p_2, p_3])
        f2.participants.extend([p_1, p_2, p_3])
        db.session.add(s2)
        db.session.add(f2)
        db.session.add_all([r_1, r_2])
        db.session.commit()

        # Should see same results for p3
        url = (url_for(FAMILY_RELATIONSHIPS_LIST_URL) +
               '?participant_id={}'.format(p3.kf_id))
        response = self.client.get(url, headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        # All family relationships returned
        self.assertEqual(len(content), 4)

    def _create_save_to_db(self):
        """
        Create and save family_relationship

        Requires creating a participant
        Create a family_relationship and add it to participant as kwarg
        Save participant
        """
        # Create study
        study = Study(external_id='phs001')

        # Create participants
        p1 = Participant(external_id='Fred', is_proband=False)
        p2 = Participant(external_id='Wilma',  is_proband=False)
        p3 = Participant(external_id='Pebbles', is_proband=True)
        p4 = Participant(external_id='Dino', is_proband=True)

        study.participants.extend([p1, p2, p3, p4])
        db.session.add(study)
        db.session.commit()

        # Create family_relationship
        kwargs = {
            'participant1_id': p1.kf_id,
            'participant2_id': p3.kf_id,
            'participant1_to_participant2_relation': 'father'
        }
        fr = FamilyRelationship(**kwargs)

        db.session.add(fr)
        db.session.commit()
        kwargs['kf_id'] = fr.kf_id
        kwargs['participant2_to_participant1_relation'] = \
            fr.participant2_to_participant1_relation

        fr.external_id = str(fr)
        db.session.commit()

        return p1, p2, p3, p4, study, kwargs
