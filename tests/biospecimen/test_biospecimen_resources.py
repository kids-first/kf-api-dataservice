import json
from urllib.parse import urlparse
from datetime import datetime
from dateutil import parser, tz

from flask import url_for

from dataservice.extensions import db
from dataservice.api.common import id_service
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from tests.utils import FlaskTestCase

BIOSPECIMENS_URL = 'api.biospecimens'
BIOSPECIMENS_LIST_URL = 'api.biospecimens_list'


class BiospecimenTest(FlaskTestCase):
    """
    Test biospecimen api
    """

    def test_post(self):
        """
        Test create a new biospecimen
        """
        kwargs = self._create_save_to_db()
        dt = datetime.now()
        # Create biospecimen data
        kwargs = {
            'external_sample_id': 's1',
            'external_aliquot_id': 'a1',
            'source_text_tissue_type': 'Normal',
            'composition': 'composition1',
            'source_text_anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'source_text_tumor_descriptor': 'Metastatic',
            'shipment_origin': 'CORIELL',
            'analyte_type': 'DNA',
            'concentration_mg_per_ml': 100,
            'volume_ml': 12.67,
            'shipment_date': str(dt.replace(tzinfo=tz.tzutc())),
            'spatial_descriptor': 'left side',
            'ncit_id_tissue_type': 'Test',
            'ncit_id_anatomical_site': 'C12439',
            'participant_id': kwargs.get('participant_id'),
            'sequencing_center_id': kwargs.get('sequencing_center_id')
        }
        # Send post request
        response = self.client.post(url_for(BIOSPECIMENS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        biospecimen = response['results']
        for k, v in kwargs.items():
            if k is 'participant_id' or k is 'sequencing_center_id':
                continue
            if k is 'shipment_date':
                self.assertEqual(parser.parse(biospecimen[k]), parser.parse(v))
            else:
                self.assertEqual(biospecimen.get(k), v)

        self.assertEqual(2, Biospecimen.query.count())

        # Test shipment_date = None
        kwargs['shipment_date'] = None
        # Send post request
        response = self.client.post(url_for(BIOSPECIMENS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())
        # Check response status status_code
        self.assertEqual(response.status_code, 201)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(3, Biospecimen.query.count())
        self.assertIs(response['results']['shipment_date'], None)

    def test_post_multiple(self):
        # Create a biospecimen with participant
        s1 = self._create_save_to_db()
        # Create another biospecimen for the same participant
        s2 = {
            'external_sample_id': 's2',
            'source_text_tissue_type': 'abnormal',
            'analyte_type': 'DNA',
            'concentration_mg_per_ml': 200,
            'volume_ml': 13.99,
            'participant_id': s1['participant_id'],
            'sequencing_center_id': s1['sequencing_center_id']
        }
        # Send post request
        response = self.client.post(url_for(BIOSPECIMENS_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(s2))
        # Check status code
        self.assertEqual(response.status_code, 201)
        # Check database
        c = Biospecimen.query.count()
        self.assertEqual(c, 2)
        biospecimens = Participant.query.all()[0].biospecimens
        self.assertEqual(len(biospecimens), 2)

    def test_get(self):
        # Create and save biospecimen to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(BIOSPECIMENS_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        biospecimen = response['results']
        participant_link = response['_links']['participant']
        participant_id = urlparse(participant_link).path.split('/')[-1]
        for k, v in kwargs.items():
            if k == 'participant_id' or k == 'sequencing_center_id':
                continue
            else:
                if isinstance(v, datetime):
                    d = v.replace(tzinfo=tz.tzutc())
                    self.assertEqual(str(parser.parse(biospecimen[k])), str(d))
                else:
                    self.assertEqual(biospecimen[k], kwargs[k])

    def test_get_all(self):
        """
        Test retrieving all biospecimens
        """
        kwargs = self._create_save_to_db()

        response = self.client.get(url_for(BIOSPECIMENS_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

    def test_patch(self):
        """
        Test updating an existing biospecimen
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')

        # Update existing biospecimen
        body = {
            'source_text_tissue_type': 'saliva',
            'participant_id': kwargs['participant_id']
        }
        response = self.client.patch(url_for(BIOSPECIMENS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('biospecimen', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        biospecimen = resp['results']
        sa = Biospecimen.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(sa, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(biospecimen.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(sa, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(str(parser.parse(biospecimen[k])), str(d))
            else:
                self.assertEqual(biospecimen[k], val)

        self.assertEqual(1, Biospecimen.query.count())

    def test_patch_bad_input(self):
        """
        Test updating an existing participant with invalid input
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')
        body = {
            'participant_id': 'AAAA1111'
        }
        response = self.client.patch(url_for(BIOSPECIMENS_URL,
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
        sa = Biospecimen.query.first()
        for k, v in kwargs.items():
            if k == 'participant_id':
                continue
            self.assertEqual(v, getattr(sa, k))

    def test_patch_missing_req_params(self):
        """
        Test create biospecimen that is missing required parameters in body
        """
        # Create and save diagnosis to db
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')
        # Create diagnosis data
        body = {
            'source_text_tissue_type': 'blood'
        }
        # Send put request
        response = self.client.patch(url_for(BIOSPECIMENS_URL,
                                             kf_id=kwargs['kf_id']),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check field values
        sa = Biospecimen.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(sa, k))

    def test_delete(self):
        """
        Test delete an existing biospecimen
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(BIOSPECIMENS_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Biospecimen.query.first()
        self.assertIs(d, None)

    def test_delete_not_found(self):
        """
        Test delete biospecimen that does not exist
        """
        kf_id = 'non-existent'
        # Send get request
        response = self.client.delete(url_for(BIOSPECIMENS_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 404)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Biospecimen.query.first()
        self.assertIs(d, None)

    def _create_save_to_db(self):
        """
        Create and save biospecimen

        Requires creating a participant
        Create a biospecimen and add it to participant as kwarg
        Save participant
        """
        dt = datetime.now()
        study = Study(external_id='phs001')
        db.session.add(study)
        db.session.commit()

        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()
        se = SequencingExperiment(external_id="Test_seq_ex_o",
                                  experiment_strategy="WGS",
                                  is_paired_end="True",
                                  platform="Test_platform",
                                  sequencing_center_id=sc.kf_id)
        db.session.add(se)
        db.session.commit()

        # Create biospecimen
        kwargs = {
            'external_sample_id': 's1',
            'external_aliquot_id': 'a1',
            'source_text_tissue_type': 'Normal',
            'composition': 'composition1',
            'source_text_anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'source_text_tumor_descriptor': 'Metastatic',
            'shipment_origin': 'CORIELL',
            'analyte_type': 'DNA',
            'concentration_mg_per_ml': 100,
            'volume_ml': 12.67,
            'shipment_date': dt,
            'spatial_descriptor': 'left side',
            'ncit_id_tissue_type': 'Test',
            'ncit_id_anatomical_site': 'C12439',
            'uberon_id_anatomical_site': 'UBERON:0000955',
            'sequencing_center_id': sc.kf_id
        }
        d = Biospecimen(**kwargs)

        # Create and save participant with biospecimen
        p = Participant(external_id='Test subject 0', biospecimens=[d],
                        is_proband=True, study_id=study.kf_id)
        db.session.add(p)
        db.session.commit()

        kwargs['participant_id'] = p.kf_id
        kwargs['kf_id'] = d.kf_id

        return kwargs
