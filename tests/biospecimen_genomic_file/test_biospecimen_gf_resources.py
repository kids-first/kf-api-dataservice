import uuid
import json
from flask import url_for

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile
)
from tests.utils import FlaskTestCase

from unittest.mock import patch
from tests.mocks import MockIndexd

BS_GF_URL = 'api.biospecimen_genomic_files'
BS_GF_LIST_URL = 'api.biospecimen_genomic_files_list'


@patch('dataservice.extensions.flask_indexd.requests')
class BiospecimenGenomicFileTest(FlaskTestCase):
    """
    Test biospecimen_genomic_file api endpoints
    """

    def test_post_biospecimen_genomic_file(self, mock):
        """
        Test creating a new biospecimen_genomic_file
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        response = self._make_biospecimen_genomic_file(mock)
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('biospecimen_genomic_file', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        # Content check
        biospecimen_genomic_file = resp['results']
        bsgf = BiospecimenGenomicFile.query.get(
            biospecimen_genomic_file['kf_id'])

        # Relations check
        bs_kfid = resp['_links']['biospecimen'].split('/')[-1]
        gf_kfid = resp['_links']['genomic_file'].split('/')[-1]
        assert bsgf.biospecimen_id == bs_kfid
        assert bsgf.genomic_file_id == gf_kfid
        assert Biospecimen.query.get(bs_kfid) is not None
        assert GenomicFile.query.get(gf_kfid) is not None

    def test_get_biospecimen_genomic_file(self, mock):
        """
        Test retrieving a biospecimen_genomic_file by id
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        resp = self._make_biospecimen_genomic_file(mock)
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(BS_GF_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        biospecimen_genomic_file = resp['results']
        bsgf = BiospecimenGenomicFile.query.get(kf_id)
        self.assertEqual(kf_id, biospecimen_genomic_file['kf_id'])
        self.assertEqual(kf_id, bsgf.kf_id)

    def test_get_all_biospecimen_genomic_files(self, mock):
        """
        Test retrieving all biospecimen_genomic_files
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        self._make_biospecimen_genomic_file(mock)

        response = self.client.get(url_for(BS_GF_LIST_URL),
                                   headers=self._api_headers())
        status_code = response.status_code
        response = json.loads(response.data.decode('utf-8'))
        content = response.get('results')
        self.assertEqual(status_code, 200)
        self.assertIs(type(content), list)
        self.assertEqual(len(content), 1)

    def test_patch_biospecimen_genomic_file(self, mock):
        """
        Test updating an existing biospecimen_genomic_file
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        response = self._make_biospecimen_genomic_file(mock)
        orig = BiospecimenGenomicFile.query.count()
        resp = json.loads(response.data.decode('utf-8'))
        biospecimen_genomic_file = resp['results']
        kf_id = biospecimen_genomic_file['kf_id']
        body = {
            # 'is_input': not biospecimen_genomic_file['is_input'],
        }
        self.assertEqual(orig, BiospecimenGenomicFile.query.count())
        response = self.client.patch(url_for(BS_GF_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        resp = json.loads(response.data.decode('utf-8'))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        self.assertIn('biospecimen_genomic_file', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        bgf = BiospecimenGenomicFile.query.get(kf_id)
        self.assertEqual(orig, BiospecimenGenomicFile.query.count())

    def test_delete_biospecimen_genomic_file(self, mock):
        """
        Test deleting a biospecimen_genomic_file by id
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        resp = self._make_biospecimen_genomic_file(mock)
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.delete(url_for(BS_GF_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())

        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BiospecimenGenomicFile.query.count(), 0)

        response = self.client.get(url_for(BS_GF_URL,
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

        # SequencingExperiment
        data = {
            'external_id': 'se',
            'experiment_strategy': 'wgs',
            'is_paired_end': True,
            'platform': 'platform',
            'sequencing_center': sc
        }
        se = SequencingExperiment(**data)
        # Genomic Files
        genomic_files = []
        for i in range(4):
            data = {
                'file_name': 'gf_{}'.format(i),
                'data_type': 'submitted aligned read',
                'file_format': '.cram',
                'urls': ['s3://file_{}'.format(i)],
                'hashes': {'md5': str(uuid.uuid4())},
                'is_harmonized': True if i % 2 else False
            }
            gf = GenomicFile(**data)
            bs.genomic_files.append(gf)
            se.genomic_files.append(gf)
            genomic_files.append(gf)

        bs2 = Biospecimen(analyte_type='rna',
                          sequencing_center=sc,
                          participant=p)
        db.session.add(bs, bs2)
        db.session.add(study)
        db.session.commit()

    def _make_biospecimen_genomic_file(self, mock, **kwargs):
        """
        Create a new biospecimen_genomic_file
        """
        # Create entities
        self._create_entities()
        bs = kwargs.get('biospecimen_id')
        gf = kwargs.get('genomic_file_id')

        if not (bs and gf):
            bs = Biospecimen.query.first().kf_id
            gf = GenomicFile.query.first().kf_id

        body = {
            'biospecimen_id': bs,
            'genomic_file_id': gf
        }

        response = self.client.post(url_for(BS_GF_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response

    def _make_multi_biospecimen_genomic_file(self, mock, **kwargs):
        """
        Create a multiple biospecimen_genomic_files
        """
        # Create entities
        self._create_entities()

        bs1 = Biospecimen.query.all()
        gf1 = GenomicFile.query.all()
        resp = []
        for bs in bs1:
            for gf in gf1:
                body = {
                    'biospecimen_id': bs.kf_id,
                    'genomic_file_id': gf.kf_id
                }
                response = self.client.post(url_for(BS_GF_LIST_URL),
                                            headers=self._api_headers(),
                                            data=json.dumps(body))
                resp.append(response)
        return resp

    def test_post_multi_biospecimen_genomic_file(self, mock):
        """
        Test creating a new biospecimen_genomic_file
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        response = self._make_multi_biospecimen_genomic_file(mock)
        resp = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(response[0].status_code, 201)
        self.assertIn('biospecimen_genomic_file', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])

        # Content check
        biospecimen_genomic_file = resp['results']
        bsgf = BiospecimenGenomicFile.query.get(
            biospecimen_genomic_file['kf_id'])

        # Relations check
        bs_kfid = resp['_links']['biospecimen'].split('/')[-1]
        gf_kfid = resp['_links']['genomic_file'].split('/')[-1]
        assert bsgf.biospecimen_id == bs_kfid
        assert bsgf.genomic_file_id == gf_kfid
        assert Biospecimen.query.get(bs_kfid) is not None
        assert GenomicFile.query.get(gf_kfid) is not None
        assert BiospecimenGenomicFile.query.count() == 8
