import uuid
import json
from flask import url_for

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.biospecimen_diagnosis.models import (
    BiospecimenDiagnosis
)
from tests.utils import FlaskTestCase

BS_DS_URL = 'api.biospecimen_diagnoses'
BS_DS_LIST_URL = 'api.biospecimen_diagnoses_list'
DIAGNOSES_URL = 'api.diagnoses'


class BiospecimenDiagnosisTest(FlaskTestCase):
    """
    Test biospecimen_diagnosis api endpoints
    """

    def test_post_biospecimen_diagnosis(self):
        """
        Test creating a new biospecimen_diagnosis
        """
        response = self._make_biospecimen_diagnosis()
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('biospecimen_diagnosis', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        # Content check
        biospecimen_diagnosis = resp['results']
        bsds = BiospecimenDiagnosis.query.get(
            biospecimen_diagnosis['kf_id'])

        # Relations check
        bs_kfid = resp['_links']['biospecimen'].split('/')[-1]
        ds_kfid = resp['_links']['diagnosis'].split('/')[-1]
        assert bsds.biospecimen_id == bs_kfid
        assert bsds.diagnosis_id == ds_kfid
        assert Biospecimen.query.get(bs_kfid) is not None
        assert Diagnosis.query.get(ds_kfid) is not None

    def test_get_biospecimen_diagnosis(self):
        """
        Test retrieving a biospecimen_diagnosis by id
        """

        resp = self._make_biospecimen_diagnosis()
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(BS_DS_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        biospecimen_diagnosis = resp['results']
        bsds = BiospecimenDiagnosis.query.get(kf_id)
        self.assertEqual(kf_id, biospecimen_diagnosis['kf_id'])
        self.assertEqual(kf_id, bsds.kf_id)

    def test_get_all_biospecimen_diagnoses(self):
        """
        Test retrieving all biospecimen_diagnoses
        """
        self._make_biospecimen_diagnosis()

        response = self.client.get(url_for(BS_DS_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_patch_biospecimen_diagnosis(self):
        """
        Test updating an existing biospecimen_diagnosis
        """
        response = self._make_biospecimen_diagnosis()
        orig = BiospecimenDiagnosis.query.count()
        resp = json.loads(response.data.decode('utf-8'))
        biospecimen_diagnosis = resp['results']
        kf_id = biospecimen_diagnosis['kf_id']
        body = {
        }
        self.assertEqual(orig, BiospecimenDiagnosis.query.count())
        response = self.client.patch(url_for(BS_DS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        resp = json.loads(response.data.decode('utf-8'))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        self.assertIn('biospecimen_diagnosis', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        bds = BiospecimenDiagnosis.query.get(kf_id)
        self.assertEqual(orig, BiospecimenDiagnosis.query.count())

    def test_delete_biospecimen_diagnosis(self):
        """
        Test deleting a biospecimen_diagnosis by id
        """

        resp = self._make_biospecimen_diagnosis()
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(BS_DS_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BiospecimenDiagnosis.query.count(), 0)

        response = self.client.get(url_for(BS_DS_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def _create_entities(self):
        """
        Create participant with required entities
        """
        # Sequencing center
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()

        # Create study
        study = Study(external_id='phs001')

        # Participants
        p = Participant(external_id='p0',
                        is_proband=True,
                        study=study)

        # Biospecimen
        bs = Biospecimen(analyte_type='dna',
                         sequencing_center=sc,
                         participant=p)
        # Diagnoses
        for i in range(4):
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
            ds = Diagnosis(**kwargs)
            p.diagnoses.append(ds)

        bs2 = Biospecimen(analyte_type='rna',
                          sequencing_center=sc,
                          participant=p)
        db.session.add(bs, bs2)
        db.session.add(study)
        db.session.commit()

    def _make_biospecimen_diagnosis(self):
        """
        Create a new biospecimen_diagnosis
        """
        # Create entities
        self._create_entities()
        bs = Biospecimen.query.first().kf_id
        ds = Diagnosis.query.first().kf_id

        body = {
            'biospecimen_id': bs,
            'diagnosis_id': ds
        }

        response = self.client.post(url_for(BS_DS_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response

    def _make_multi_biospecimen_diagnosis(self):
        """
        Create a multiple biospecimen_diagnoses
        """
        # Create entities
        self._create_entities()

        bs1 = Biospecimen.query.all()
        ds1 = Diagnosis.query.all()
        resp = []
        for bs in bs1:
            for ds in ds1:
                body = {
                    'biospecimen_id': bs.kf_id,
                    'diagnosis_id': ds.kf_id
                }
                response = self.client.post(url_for(BS_DS_LIST_URL),
                                            headers=self._api_headers(),
                                            data=json.dumps(body))
                resp.append(response)
        return resp

    def test_post_multi_biospecimen_diagnosis(self):
        """
        Test creating a new biospecimen_diagnosis
        """

        response = self._make_multi_biospecimen_diagnosis()
        resp = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(response[0].status_code, 201)
        self.assertIn('biospecimen_diagnosis', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        # Content check
        biospecimen_diagnosis = resp['results']
        bsds = BiospecimenDiagnosis.query.get(
            biospecimen_diagnosis['kf_id'])

        # Relations check
        bs_kfid = resp['_links']['biospecimen'].split('/')[-1]
        ds_kfid = resp['_links']['diagnosis'].split('/')[-1]
        assert bsds.biospecimen_id == bs_kfid
        assert bsds.diagnosis_id == ds_kfid
        assert Biospecimen.query.get(bs_kfid) is not None
        assert Diagnosis.query.get(ds_kfid) is not None
        assert BiospecimenDiagnosis.query.count() == 8

    def test_invalid_biospecimen(self):
        """
        Test that a diagnosis cannot be linked with a biospecimen if
        they refer to different participants
        """
        self._create_entities()
        p0 = Participant.query.first().kf_id

        # Create new participant with biospecimen
        st = Study.query.first()
        s = SequencingCenter.query.first()
        p1 = Participant(external_id='p1', is_proband=True, study_id=st.kf_id)
        b = Biospecimen(analyte_type='DNA',
                        sequencing_center_id=s.kf_id,
                        participant=p1)
        db.session.add(b)
        db.session.commit()

        # Update existing diagnosis
        d0 = Diagnosis.query.first().kf_id
        body = {
            'source_text_diagnosis': 'hangry',
            'diagnosis_category': 'Structural Birth Defect',
            'participant_id': p1.kf_id
        }
        response = self.client.patch(url_for(DIAGNOSES_URL,
                                             kf_id=d0),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        b0 = Biospecimen.query.first().kf_id
        body = {'biospecimen_id': b0,
                'diagnosis_id': d0}
        response = self.client.post(url_for(BS_DS_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 400)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        assert 'could not modify biospecimen_diagnosis' in resp['_status'
                                                                ]['message']
        assert 'diagnosis {}'.format(d0) in resp['_status']['message']
        assert ('participant {}'.format(p0)
                in resp['_status']['message'])
