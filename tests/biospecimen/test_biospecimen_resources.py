import json
from urllib.parse import urlparse, urlencode
from datetime import datetime
from dateutil import parser, tz

from flask import url_for

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import (
    Biospecimen,
    BiospecimenDiagnosis,
    BiospecimenGenomicFile
)
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter

from tests.utils import IndexdTestCase

BIOSPECIMENS_URL = 'api.biospecimens'
BIOSPECIMENS_LIST_URL = 'api.biospecimens_list'


class BiospecimenTest(IndexdTestCase):
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
            'duo_ids': ['DUO:0000021', 'DUO:0000005'],
            'source_text_tissue_type': 'Normal',
            'composition': 'composition1',
            'source_text_anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'source_text_tumor_descriptor': 'Metastatic',
            'shipment_origin': 'CORIELL',
            'analyte_type': 'DNA',
            'concentration_mg_per_ml': 100,
            'volume_ul': 12.67,
            "amount": 112.67,
            "amount_units": "ul",
            'shipment_date': str(dt.replace(tzinfo=tz.tzutc())),
            'spatial_descriptor': 'left side',
            'ncit_id_tissue_type': 'Test',
            'ncit_id_anatomical_site': 'C12439',
            'participant_id': kwargs.get('participant_id'),
            'consent_type': 'GRU-IRB',
            'dbgap_consent_code': 'phs00000.c1',
            'sequencing_center_id': kwargs.get('sequencing_center_id'),
            'preservation_method': 'Fresh',
            'specimen_status': 'Not Available',
            'has_matched_normal_sample': True
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
            'volume_ul': 13.99,
            "amount": 13.99,
            "amount_units": "ul",
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
            'participant_id': kwargs['participant_id'],
            'duo_ids': ['DUO:0000021', 'DUO:0000005'],
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

    def test_filters(self):
        """
        Test get and filter diagnosis by biospecimen_id or study id
        """
        self._create_all_entities()

        assert 8 == Diagnosis.query.count()
        assert 8 == Biospecimen.query.count()
        assert 5 == BiospecimenDiagnosis.query.count()
        assert 6 == GenomicFile.query.count()
        assert 8 == BiospecimenGenomicFile.query.count()

        # Create query - Participant p0, Diagnosis d2 has 2 biospecimens
        d = Diagnosis.query.filter_by(external_id='study0-p0-d2').first()
        s = Study.query.filter_by(external_id='s0').first()
        bds = BiospecimenDiagnosis.query.filter_by(
            diagnosis_id=d.kf_id).count()
        gf = GenomicFile.query.filter_by(external_id='study0-b0-gf0').first()
        bsgf = BiospecimenGenomicFile.query.filter_by(
            genomic_file_id=gf.kf_id).count()
        assert bds == 2
        assert bsgf == 2

        # test study_id filter
        filter_params = {'study_id': s.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/biospecimens', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 4 == response['total']
        assert 4 == len(response['results'])
        results = response['results']
        for r in results:
            assert r['external_sample_id'] in {'study0-p0-b0',
                                               'study0-p0-b1',
                                               'study0-p1-b0',
                                               'study0-p2-b0'}
        # Send genomic_file_id
        filter_params = {'genomic_file_id': gf.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/biospecimens', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 2 == response['total']
        assert 2 == len(response['results'])
        results = response['results']
        for r in results:
            assert r['external_sample_id'] in {'study0-p0-b0',
                                               'study0-p0-b1'}

        # test diagnois_id filter
        filter_params = {'diagnosis_id': d.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/biospecimens', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 2 == response['total']
        assert 2 == len(response['results'])
        results = response['results']
        for r in results:
            assert r['external_sample_id'] in {'study0-p0-b0',
                                               'study0-p0-b1'}

        # Send get request
        filter_params = {'diagnosis_id': d.kf_id,
                         'study_id': s.kf_id,
                         'genomic_file_id': gf.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/biospecimens', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 2 == response['total']
        assert 2 == len(response['results'])
        results = response['results']
        for r in results:
            assert r['external_sample_id'] in {'study0-p0-b0',
                                               'study0-p0-b1'}

        # Create query - Participant p1, Diagnosis d0 has 1 biospecimens
        d = Diagnosis.query.filter_by(external_id='study0-p1-d0').first()
        s = Study.query.filter_by(external_id='s0').first()
        bds = BiospecimenDiagnosis.query.filter_by(
            diagnosis_id=d.kf_id).count()
        gf = GenomicFile.query.filter_by(external_id='study0-b1-gf0').first()
        bsgf = BiospecimenGenomicFile.query.filter_by(
            genomic_file_id=gf.kf_id).count()
        assert bds == 1
        assert bsgf == 1

        # Send get request
        filter_params = {'diagnosis_id': d.kf_id,
                         'study_id': s.kf_id,
                         'genomic_file_id': gf.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/biospecimens', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 1 == response['total']
        assert 1 == len(response['results'])
        results = response['results']
        for r in results:
            assert r['external_sample_id'] in {'study0-p1-b0'}

        # Create query - Same as first query, but wrong study yields 0 results
        d = Diagnosis.query.filter_by(external_id='study0-p0-d2').first()
        s = Study.query.filter_by(external_id='s1').first()
        bds = BiospecimenDiagnosis.query.filter_by(
            diagnosis_id=d.kf_id).count()
        assert bds == 2

        # Send get request
        filter_params = {'diagnosis_id': d.kf_id,
                         'study_id': s.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/biospecimens', qs)
        response = self.client.get(endpoint, headers=self._api_headers())
        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 0 == response['total']
        assert 0 == len(response['results'])

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
            'duo_ids': ['DUO:0000021'],
            'source_text_tissue_type': 'Normal',
            'composition': 'composition1',
            'source_text_anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'source_text_tumor_descriptor': 'Metastatic',
            'shipment_origin': 'CORIELL',
            'analyte_type': 'DNA',
            'concentration_mg_per_ml': 100,
            'volume_ul': 12.67,
            "amount": 12.67,
            "amount_units": "ul",
            'shipment_date': dt,
            'spatial_descriptor': 'left side',
            'ncit_id_tissue_type': 'Test',
            'ncit_id_anatomical_site': 'C12439',
            'uberon_id_anatomical_site': 'UBERON:0000955',
            'consent_type': 'GRU-IRB',
            'dbgap_consent_code': 'phs00000.c1',
            'sequencing_center_id': sc.kf_id,
            'has_matched_normal_sample': True
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
            gf = GenomicFile(
                external_id='study{}-b0-gf0'.format(j),
                urls=['s3://mybucket/key'],
                hashes={'md5': 'd418219b883fce3a085b1b7f38b01e37'})
            for i in range(2):
                b = Biospecimen(
                    external_sample_id='study{}-p0-b{}'.format(j, i),
                    analyte_type='DNA',
                    sequencing_center=sc)
                b.genomic_files.append(gf)
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
                    gf = GenomicFile(
                        external_id='study{}-b0-gf{}'.format(j, k + 1),
                        urls=['s3://mybucket/key'],
                        hashes={'md5': 'd418219b883fce3a085b1b7f38b01e37'})
                    b.genomic_files.append(gf)
                    p0.diagnoses.append(d)
                p0.biospecimens.append(b)

            # Participant 1
            # Has 1 biospecimen, 1 diagnosis
            b = Biospecimen(external_sample_id='study{}-p1-b0'.format(j),
                            analyte_type='DNA',
                            sequencing_center=sc)
            d = Diagnosis(external_id='study{}-p1-d0'.format(j))
            gf = GenomicFile(
                external_id='study{}-b1-gf0'.format(j),
                urls=['s3://mybucket/key'],
                hashes={'md5': 'd418219b883fce3a085b1b7f38b01e37'})
            b.genomic_files.append(gf)
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
