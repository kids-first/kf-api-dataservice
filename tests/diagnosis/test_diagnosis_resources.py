import json

from flask import url_for
from urllib.parse import urlparse
from datetime import datetime
from dateutil import parser, tz
from urllib.parse import urlencode

from dataservice.extensions import db
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import (
    Biospecimen,
    BiospecimenDiagnosis
)
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

DIAGNOSES_URL = 'api.diagnoses'
DIAGNOSES_LIST_URL = 'api.diagnoses_list'


class DiagnosisTest(FlaskTestCase):
    """
    Test diagnosis api
    """

    def test_post(self):
        """
        Test create a new diagnosis
        """
        kwargs = self._create_save_to_db()

        # Create diagnosis data
        kwargs = {
            'external_id': 'd1',
            'source_text_diagnosis': 'flu',
            'age_at_event_days': 365,
            'diagnosis_category': 'Cancer',
            'source_text_tumor_location': 'Brain',
            'mondo_id_diagnosis': 'DOID:8469',
            'icd_id_diagnosis': 'J10.01',
            'uberon_id_tumor_location': 'UBERON:0000955',
            'spatial_descriptor': 'left side',
            'participant_id': kwargs.get('participant_id')
        }
        # Send get request
        response = self.client.post(url_for(DIAGNOSES_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        diagnosis = response['results']
        dg = Diagnosis.query.get(diagnosis.get('kf_id'))
        for k, v in kwargs.items():
            if k == 'participant_id':
                continue
            self.assertEqual(diagnosis[k], getattr(dg, k))
        self.assertEqual(2, Diagnosis.query.count())

    def test_post_multiple(self):
        # Create a diagnosis with participant
        d1 = self._create_save_to_db()
        # Create another diagnosis for the same participant
        d2 = {
            'external_id': 'd2',
            'source_text_diagnosis': 'cold',
            'diagnosis_category': 'Cancer',
            'source_text_tumor_location': 'Brain',
            'mondo_id_diagnosis': 'DOID:8469',
            'icd_id_diagnosis': 'J10.01',
            'uberon_id_tumor_location': 'UBERON:0000955',
            'spatial_descriptor': 'left side',
            'participant_id': d1['participant_id']
        }
        # Send post request
        response = self.client.post(url_for(DIAGNOSES_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(d2))
        # Check status code
        self.assertEqual(response.status_code, 201)
        # Check database
        c = Diagnosis.query.count()
        self.assertEqual(c, 2)
        pd = Participant.query.all()[0].diagnoses
        self.assertEqual(len(pd), 2)

    def test_get(self):
        # Create and save diagnosis to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(DIAGNOSES_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        diagnosis = response['results']
        participant_link = response['_links']['participant']
        participant_id = urlparse(participant_link).path.split('/')[-1]
        for k, v in kwargs.items():
            if k == 'participant_id':
                self.assertEqual(participant_id,
                                 kwargs['participant_id'])
            else:
                self.assertEqual(diagnosis[k], diagnosis[k])

    def test_get_all(self):
        """
        Test retrieving all diagnoses
        """
        kwargs = self._create_save_to_db()

        response = self.client.get(url_for(DIAGNOSES_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        self.assertEqual(len(content), 1)

    def test_patch(self):
        """
        Test updating an existing diagnosis
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')

        # Update existing diagnosis
        body = {
            'source_text_diagnosis': 'hangry',
            'diagnosis_category': 'Structural Birth Defect',
            'participant_id': kwargs['participant_id']
        }
        response = self.client.patch(url_for(DIAGNOSES_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('diagnosis', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        diagnosis = resp['results']
        dg = Diagnosis.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(dg, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(diagnosis.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(dg, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(str(parser.parse(diagnosis[k])), str(d))
            else:
                self.assertEqual(diagnosis[k], val)

        self.assertEqual(1, Diagnosis.query.count())

    def test_delete(self):
        """
        Test delete an existing diagnosis
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(DIAGNOSES_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Diagnosis.query.first()
        self.assertIs(d, None)

    def test_patch_diagnosis_w_biospecimen(self):
        """
        Test update diagnosis with biospecimen
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')
        biospecimen = Biospecimen.query.first()
        # Update existing diagnosis
        body = {
            'biospecimens': [{'kf_id': biospecimen.kf_id}]
        }
        response = self.client.patch(url_for(DIAGNOSES_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('diagnosis', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Update existing diagnosis with wrong format
        # biospecimens takes dictionary with key as kf_id
        body = {
            'biospecimens': [biospecimen.kf_id]
        }
        response = self.client.patch(url_for(DIAGNOSES_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        resp = json.loads(response.data.decode("utf-8"))
        # Status code
        self.assertEqual(response.status_code, 400)
        self.assertIn('could not update diagnosis', resp['_status']['message'])

        # Update existing diagnosis with non existing bisopecimen id
        # biospecimens takes dictionary with key as kf_id
        body = {
            'biospecimens': [{'kf_id': 'BS_00000000'}]
        }
        response = self.client.patch(url_for(DIAGNOSES_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        resp = json.loads(response.data.decode("utf-8"))
        # Status code
        self.assertEqual(response.status_code, 400)
        self.assertIn('could not modify', resp['_status']['message'])
        self.assertIn('does not exist', resp['_status']['message'])

        sequencing_center_id = SequencingCenter.query.first()
        b = Biospecimen(analyte_type='DNA',
                        sequencing_center_id=sequencing_center_id.kf_id,
                        participant_id=kwargs['participant_id'])
        db.session.add(b)
        db.session.commit()

        # Update existing diagnosis with multiple bisopecimens
        # biospecimens takes dictionary with key as kf_id
        body = {
            'biospecimens': [{'kf_id': biospecimen.kf_id},
                             {'kf_id': b.kf_id}]
        }
        response = self.client.patch(url_for(DIAGNOSES_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('diagnosis', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])
        self.assertEqual(1, Diagnosis.query.count())
        self.assertEqual(2, Biospecimen.query.count())
        self.assertEqual([biospecimen, b],
                         Diagnosis.query.first().biospecimens)

        body = {
            'biospecimens': []
        }
        response = self.client.patch(url_for(DIAGNOSES_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(1, Diagnosis.query.count())
        self.assertEqual(2, Biospecimen.query.count())
        self.assertEqual([],
                         Diagnosis.query.first().biospecimens)

    def test_filters(self):
        """
        Test get and filter diagnoses by biospecimen_id or study id
        """
        self._create_all_entities()

        assert 8 == Diagnosis.query.count()
        assert 8 == Biospecimen.query.count()
        assert 5 == BiospecimenDiagnosis.query.count()

        # Create query - Participant p0, Biospecimen b0 has 3 diagnoses
        bs = Biospecimen.query.filter_by(
            external_sample_id='study0-p0-b0').first()
        s = Study.query.filter_by(external_id='s0').first()
        assert len(bs.diagnoses) == 3

        # Send get request
        filter_params = {'biospecimen_id': bs.kf_id,
                         'study_id': s.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/diagnoses', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 3 == response['total']
        assert 3 == len(response['results'])
        diagnoses = response['results']
        for d in diagnoses:
            assert d['external_id'] in {'study0-p0-d0',
                                        'study0-p0-d1',
                                        'study0-p0-d2'}

        # Create query - Participant p0, Biospecimen b1 has 1 diagnosis
        bs = Biospecimen.query.filter_by(
            external_sample_id='study0-p0-b1').first()
        assert len(bs.diagnoses) == 1

        # Send get request
        filter_params = {'biospecimen_id': bs.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/diagnoses', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 1 == response['total']
        assert 1 == len(response['results'])
        diagnoses = response['results']
        for d in diagnoses:
            assert d['external_id'] in {'study0-p0-d2'}

        # Create query - Same as first query but wrong study, yields 0 results
        bs = Biospecimen.query.filter_by(
            external_sample_id='study0-p0-b0').first()
        s = Study.query.filter_by(external_id='s1').first()
        assert len(bs.diagnoses) == 3

        # Send get request
        filter_params = {'biospecimen_id': bs.kf_id,
                         'study_id': s.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/diagnoses', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 0 == response['total']
        assert 0 == len(response['results'])

    def _create_save_to_db(self):
        """
        Create and save diagnosis

        Requires creating a participant
        Create a diagnosis and add it to participant as kwarg
        Save participant
        """
        # Create study
        study = Study(external_id='phs001')

        # Create diagnosis
        kwargs = {
            'external_id': 'd1',
            'source_text_diagnosis': 'flu',
            'diagnosis_category': 'Cancer',
            'source_text_tumor_location': 'Brain',
            'age_at_event_days': 365,
            'mondo_id_diagnosis': 'DOID:8469',
            'icd_id_diagnosis': 'J10.01',
            'uberon_id_tumor_location': 'UBERON:0000955',
            'spatial_descriptor': 'left side'
        }
        d = Diagnosis(**kwargs)

        # Create and save participant with diagnosis
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, diagnoses=[d],
                        is_proband=True, study=study)
        db.session.add(p)
        db.session.commit()

        # Create sequencing center
        s = SequencingCenter(name='washu')
        db.session.add(s)
        db.session.commit()
        # Create biospecimen
        b = Biospecimen(analyte_type='DNA',
                        sequencing_center_id=s.kf_id,
                        participant=p)
        db.session.add(s)
        db.session.add(b)
        db.session.commit()

        kwargs['participant_id'] = p.kf_id
        kwargs['kf_id'] = d.kf_id

        return kwargs

    def _create_all_entities(self):
        """
        Create 2 studies with same content
        Content: 3 participants, 4 biospecimens, 4 diagnoses
        """
        # Create entities
        sc = SequencingCenter.query.filter_by(name='sc').first()
        if not sc:
            sc = SequencingCenter(name='sc')
        studies = []

        # Two studies
        for j in range(2):
            s = Study(external_id='s{}'.format(j))
            p0 = Participant(external_id='study{}-p0'.format(j))
            p1 = Participant(external_id='study{}-p1'.format(j))
            p2 = Participant(external_id='study{}-p2'.format(j))

            # Participant 0
            # Has 2 Biospecimens
            for i in range(2):
                b = Biospecimen(
                    external_sample_id='study{}-p0-b{}'.format(j, i),
                    analyte_type='DNA',
                    sequencing_center=sc)

                # Biospecimen b0 has 2 diagnoses
                if i == 0:
                    for k in range(2):
                        d = Diagnosis(
                            external_id='study{}-p0-d{}'.format(j, k))
                        p0.diagnoses.append(d)

                # Biospecimen b1 has 1 diagnosis
                else:
                    d = Diagnosis(
                        external_id='study{}-p0-d{}'.format(j, k + 1))
                    p0.diagnoses.append(d)
                p0.biospecimens.append(b)

            # Participant 1
            # Has 1 biospecimen, 1 diagnosis
            b = Biospecimen(external_sample_id='study{}-p1-b0'.format(j),
                            analyte_type='DNA',
                            sequencing_center=sc)
            d = Diagnosis(external_id='study{}-p1-d0'.format(j))
            p1.biospecimens.append(b)
            p1.diagnoses.append(d)

            # Participant 2
            # Has 1 biospecimen
            b = Biospecimen(external_sample_id='study{}-p2-b0'.format(j),
                            analyte_type='DNA',
                            sequencing_center=sc)
            p2.biospecimens.append(b)

            s.participants.extend([p0, p1, p2])
            studies.append(s)

        db.session.add_all(studies)
        db.session.commit()

        # Create links between bios and diags
        bs_dgs = []

        # Participant 0
        p0 = studies[0].participants[0]
        # b0-d0
        bs_dgs.append(
            BiospecimenDiagnosis(biospecimen_id=p0.biospecimens[0].kf_id,
                                 diagnosis_id=p0.diagnoses[0].kf_id))
        # b0-d1
        bs_dgs.append(
            BiospecimenDiagnosis(biospecimen_id=p0.biospecimens[0].kf_id,
                                 diagnosis_id=p0.diagnoses[1].kf_id))
        # b1-d2
        bs_dgs.append(
            BiospecimenDiagnosis(biospecimen_id=p0.biospecimens[1].kf_id,
                                 diagnosis_id=p0.diagnoses[2].kf_id))
        # b0-d2
        bs_dgs.append(
            BiospecimenDiagnosis(biospecimen_id=p0.biospecimens[0].kf_id,
                                 diagnosis_id=p0.diagnoses[2].kf_id))

        # Participant 1
        p1 = studies[0].participants[1]
        # b0-d0
        bs_dgs.append(
            BiospecimenDiagnosis(biospecimen_id=p1.biospecimens[0].kf_id,
                                 diagnosis_id=p1.diagnoses[0].kf_id))

        db.session.add_all(bs_dgs)
        db.session.commit()
