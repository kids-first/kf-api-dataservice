import json

from flask import url_for
from urllib.parse import urlparse
from datetime import datetime
from dateutil import parser, tz

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

BIO_DIAG_URL = 'api.biospecimen_diagnoses'
BIO_DIAG_LIST_URL = 'api.biospecimen_diagnoses_list'


class BiospecimenDiagnosisTest(FlaskTestCase):
    """
    Test biospecimen_diagnosis api
    """

    def test_post(self):
        """
        Test create a new biospecimen_diagnosis
        """
        self._create_all_entities(link_bio=False)

        # Create biospecimen diagnosis data
        p = Participant.query.first()
        kwargs = {
            'biospecimen_id': p.biospecimens[0].kf_id,
            'diagnosis_id': p.diagnoses[0].kf_id
        }
        # Send get request
        response = self.client.post(url_for(BIO_DIAG_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 'kf_id' in response['results']
        assert 1 == BiospecimenDiagnosis.query.count()

    def test_post_invalid(self):
        """
        Test create a biospecimen_diagnosis with a bio and diag from two
        different participants
        """
        self._create_all_entities(link_bio=False)

        # Create biospecimen diagnosis data
        participants = Participant.query.all()
        kwargs = {
            'biospecimen_id': participants[0].biospecimens[0].kf_id,
            'diagnosis_id': participants[1].diagnoses[0].kf_id
        }
        # Send get request
        response = self.client.post(url_for(BIO_DIAG_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 400)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        response = response['_status']
        assert 400 == response['code']
        assert 'cannot be linked with' in response['message']
        assert 0 == BiospecimenDiagnosis.query.count()

    def test_get(self):
        """
        Test get biospecimen_diagnosis
        """
        # Create entities
        self._create_all_entities()
        kf_id = BiospecimenDiagnosis.query.first().kf_id

        # Send get request
        response = self.client.get(url_for(BIO_DIAG_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert kf_id == response['results']['kf_id']

    def test_get_all(self):
        """
        Test retrieving all biospecimen_diagnoses
        """
        self._create_all_entities()

        response = self.client.get(url_for(BIO_DIAG_LIST_URL),
                                   headers=self._api_headers())
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode("utf-8"))
        content = response.get('results')
        assert 5 == len(content)
        assert 5 == BiospecimenDiagnosis.query.count()

    def test_patch(self):
        """
        Test updating an existing biospecimen_diagnosis
        """
        self._create_all_entities()
        kf_id = BiospecimenDiagnosis.query.first().kf_id

        # Update existing
        body = {
            'external_id': 'bd'
        }
        response = self.client.patch(url_for(BIO_DIAG_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('biospecimen_diagnosis', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        res = resp['results']
        bd = BiospecimenDiagnosis.query.get(kf_id)
        assert bd.external_id == res['external_id']

    def test_patch_invalid(self):
        """
        Test patch a biospecimen_diagnosis by linking a bio and diag from two
        different participants
        """
        self._create_all_entities(link_bio=False)

        # Create a valid one first
        participants = Participant.query.all()
        kwargs = {
            'biospecimen_id': participants[0].biospecimens[0].kf_id,
            'diagnosis_id': participants[0].diagnoses[0].kf_id
        }
        bd = BiospecimenDiagnosis(**kwargs)
        db.session.add(bd)
        db.session.commit()

        # Patch it with invalid data
        patch_kwargs = {
            'biospecimen_id': participants[1].biospecimens[0].kf_id
        }
        # Send get request
        response = self.client.patch(url_for(BIO_DIAG_URL,
                                             kf_id=bd.kf_id),
                                     data=json.dumps(patch_kwargs),
                                     headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 400)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        response = response['_status']
        assert 400 == response['code']
        assert 'cannot be linked with' in response['message']
        bd = BiospecimenDiagnosis.query.first()

        # Check db - nothing should have updated
        for k, v in kwargs.items():
            assert getattr(bd, k) == v

    def test_delete(self):
        """
        Test delete an existing biospecimen_diagnosis
        """
        self._create_all_entities()
        kf_id = BiospecimenDiagnosis.query.first().kf_id

        # Send get request
        response = self.client.delete(url_for(BIO_DIAG_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        assert BiospecimenDiagnosis.query.get(kf_id) is None

    def _create_all_entities(self, link_bio=True):
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

        if link_bio:
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
