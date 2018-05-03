import json
from flask import url_for
from urllib.parse import urlparse

from dataservice.extensions import db
from dataservice.api.common import id_service
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

PHENOTYPES_URL = 'api.phenotypes'
PHENOTYPES_LIST_URL = 'api.phenotypes_list'


class PhenotypeTest(FlaskTestCase):
    """
    Test phenotype api
    """

    def test_post(self):
        """
        Test create a new phenotype
        """
        # Create study
        study = Study(external_id='phs001')

        # Create a participant
        p = Participant(external_id='Test subject 0', is_proband=True,
                        study=study)
        db.session.add(p)
        db.session.commit()

        # Create phenotype data
        kwargs = {
            'external_id': 'test_phenotype_0',
            'source_text_phenotype': 'Hand tremor',
            'age_at_event_days': 365,
            'hpo_id_phenotype': 'HP:0002378',
            'observed': 'positive',
            'participant_id': p.kf_id
        }
        # Send get request
        response = self.client.post(url_for(PHENOTYPES_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        phenotype = response['results']
        ph = Phenotype.query.get(phenotype.get('kf_id'))
        for k, v in kwargs.items():
            if k == 'participant_id':
                continue
            self.assertEqual(phenotype[k], getattr(ph, k))

    def test_post_multiple(self):
        # Create a phenotype with participant
        ph1 = self._create_save_to_db()
        # Create another phenotype for the same participant
        ph2 = {
            'external_id': 'test_phenotype_1',
            'source_text_phenotype': 'Tall stature',
            'hpo_id_phenotype': 'HP:0000098',
            'snomed_id_phenotype': '38033009',
            'observed': 'positive',
            'participant_id': ph1['participant_id']
        }
        # Send post request
        response = self.client.post(url_for(PHENOTYPES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(ph2))
        # Check status code
        self.assertEqual(response.status_code, 201)
        # Check database
        phe = Phenotype.query.count()
        self.assertEqual(phe, 2)
        pph = Participant.query.all()[0].phenotypes
        self.assertEqual(len(pph), 2)

    def test_get(self):
        # Create and save phenotype to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(PHENOTYPES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        phenotype = response['results']
        participant_link = response['_links']['participant']
        participant_id = urlparse(participant_link).path.split('/')[-1]
        for k, v in kwargs.items():
            if k == 'participant_id':
                continue
            self.assertEqual(phenotype[k], v)

    def test_get_all(self):
        """
        Test retrieving all phenotypes
        """
        kwargs = self._create_save_to_db()

        response = self.client.get(url_for(PHENOTYPES_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

    def test_patch(self):
        """
        Test update existing phenotype
        """
        kwargs = self._create_save_to_db()

        # Send patch request
        body = {
            'source_text_phenotype': 'Tall stature',
            'hpo_id_phenotype': 'HP:0002378',
            'participant_id': kwargs['participant_id']
        }
        response = self.client.patch(url_for(PHENOTYPES_URL,
                                             kf_id=kwargs['kf_id']),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check field values got updated
        response = json.loads(response.data.decode('utf-8'))
        phenotype = response['results']
        self.assertEqual(kwargs['kf_id'], phenotype['kf_id'])

        # Fields that should be updated w values
        self.assertEqual(body['source_text_phenotype'],
                         phenotype['source_text_phenotype'])
        self.assertEqual(body['hpo_id_phenotype'],
                         phenotype['hpo_id_phenotype'])

    def test_delete(self):
        """
        Test delete an existing phenotype
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(PHENOTYPES_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        p = Phenotype.query.first()
        self.assertIs(p, None)

    def _create_save_to_db(self):
        """
        Create and save phenotype

        Requires creating a participant
        Create a phenotype and add it to participant as kwarg
        Save participant
        """
        # Create study
        study = Study(external_id='phs001')

        # Create phenotype
        kwargs = {
            'external_id': 'test_phenotype_0',
            'source_text_phenotype': 'Hand Tremor',
            'hpo_id_phenotype': 'HP:0002378',
            'snomed_id_phenotype': '38033009',
            'observed': 'positive',
            'age_at_event_days': 365
        }
        ph = Phenotype(**kwargs)

        # Create and save participant with phenotype
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, phenotypes=[ph],
                        is_proband=True, study=study)
        db.session.add(p)
        db.session.commit()

        kwargs['participant_id'] = p.kf_id
        kwargs['kf_id'] = ph.kf_id

        return kwargs
