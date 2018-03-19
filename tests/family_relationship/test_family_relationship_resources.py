import json
from flask import url_for
from urllib.parse import urlparse
from sqlalchemy import or_

from dataservice.extensions import db
from dataservice.api.family_relationship.models import FamilyRelationship
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
        kwargs = self._create_save_to_db()

        # Create new family relationship
        results = Participant.query.filter(
            or_
            (Participant.external_id == 'Pebbles',
             Participant.external_id == 'Dino'))
        kwargs = {
            'participant_id': results[0].kf_id,
            'relative_id': results[1].kf_id,
            'participant_to_relative_relation': 'father'
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
            if k == 'participant_id':
                self.assertEqual(v, kwargs.get('participant_id'))
            elif k == 'relative_id':
                self.assertEqual(v, kwargs.get('relative_id'))
            else:
                self.assertEqual(family_relationship[k], getattr(fr, k))
        self.assertEqual(2, FamilyRelationship.query.count())

    def test_get(self):
        # Create and save family_relationship to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(FAMILY_RELATIONSHIPS_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        family_relationship = response['results']
        participant_link = response['_links']['participant']
        participant_id = urlparse(participant_link).path.split('/')[-1]
        relative_link = response['_links']['relative']
        relative_id = urlparse(relative_link).path.split('/')[-1]
        for k, v in kwargs.items():
            if k == 'participant_id':
                self.assertEqual(participant_id,
                                 kwargs['participant_id'])
            elif k == 'relative_id':
                self.assertEqual(relative_id,
                                 kwargs['relative_id'])
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
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')

        # Update existing family_relationship
        body = {
            'participant_to_relative_relation': 'mother'
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
        self.assertEqual(kwargs.get('relative_to_participant_relation'),
                         family_relationship.get(
                         'relative_to_participant_relation'))
        self.assertEqual(1, FamilyRelationship.query.count())

    def test_delete(self):
        """
        Test delete an existing family_relationship
        """
        kwargs = self._create_save_to_db()
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
        p2 = Participant(external_id='Pebbles',  is_proband=True)
        p3 = Participant(external_id='Pebbles', is_proband=True)
        p4 = Participant(external_id='Dino', is_proband=False)

        study.participants.extend([p1, p2, p3, p4])
        db.session.add(study)
        db.session.commit()

        # Create family_relationship
        kwargs = {
            'participant_id': p1.kf_id,
            'relative_id': p2.kf_id,
            'participant_to_relative_relation': 'father'
        }
        fr = FamilyRelationship(**kwargs)

        db.session.add(fr)
        db.session.commit()
        kwargs['kf_id'] = fr.kf_id
        kwargs['relative_to_participant_relation'] = \
            fr.relative_to_participant_relation

        return kwargs
