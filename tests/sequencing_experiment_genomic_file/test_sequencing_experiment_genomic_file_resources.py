import json
from datetime import datetime

from flask import url_for
from dateutil import parser, tz

from dataservice.extensions import db
from dataservice.api.sequencing_experiment.models import (
    SequencingExperiment,
    SequencingExperimentGenomicFile
)
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_center.models import SequencingCenter
from tests.utils import IndexdTestCase

SE_GF_URL = 'api.sequencing_experiment_genomic_files'
SE_GF_LIST_URL = 'api.sequencing_experiment_genomic_files_list'


class SequencingExperimentGenomicFileTest(IndexdTestCase):
    """
    Test sequencing_experiment_genomic_file api
    """

    def test_post(self):
        """
        Test create a new sequencing_experiment_genomic_file
        """
        # Create needed entities
        gf = GenomicFile(external_id='gf0')
        sc = SequencingCenter(external_id='sc')
        se = SequencingExperiment(external_id='se0',
                                  experiment_strategy='WGS',
                                  is_paired_end=True,
                                  platform='platform',
                                  sequencing_center=sc)
        db.session.add_all([gf, se])
        db.session.commit()

        kwargs = {'sequencing_experiment_id': se.kf_id,
                  'genomic_file_id': gf.kf_id,
                  'external_id': 'se0-gf0'
                  }

        # Send get request
        response = self.client.post(url_for(SE_GF_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert response['results']['kf_id']
        self.assertEqual(1, SequencingExperimentGenomicFile.query.count())

    def test_get(self):
        """
        Test retrieval of sequencing_experiment_genomic_file
        """
        # Create and save sequencing_experiment to db
        ses, ses = self._create_save_to_db()
        segf = SequencingExperimentGenomicFile.query.first()
        # Send get request
        response = self.client.get(url_for(SE_GF_URL,
                                           kf_id=segf.kf_id),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sequencing_experiment_gf = response['results']
        for k, v in sequencing_experiment_gf.items():
            attr = getattr(segf, k)
            if isinstance(attr, datetime):
                attr = attr.replace(tzinfo=tz.tzutc()).isoformat()
            self.assertEqual(sequencing_experiment_gf[k], attr)

    def test_patch(self):
        """
        Test partial update of an existing sequencing_experiment_genomic_file
        """
        ses, gfs = self._create_save_to_db()
        segf = SequencingExperimentGenomicFile.query.first()

        # Update existing sequencing_experiment
        body = {'external_id': 'updated'}

        response = self.client.patch(url_for(SE_GF_URL,
                                             kf_id=segf.kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('sequencing_experiment', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        sequencing_experiment_gf = resp['results']
        for k, v in body.items():
            self.assertEqual(v, getattr(segf, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(sequencing_experiment_gf.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(segf, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(
                    str(parser.parse(sequencing_experiment_gf[k])), str(d))
            else:
                self.assertEqual(sequencing_experiment_gf[k], val)

        # Check counts
        self.assertEqual(4, SequencingExperimentGenomicFile.query.count())

    def test_delete(self):
        """
        Test delete an existing sequencing_experiment_genomic_file
        """
        ses, gfs = self._create_save_to_db()
        kf_id = SequencingExperimentGenomicFile.query.first().kf_id

        # Send get request
        response = self.client.delete(url_for(SE_GF_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        segf = SequencingExperimentGenomicFile.query.get(kf_id)
        self.assertIs(segf, None)

    def _create_save_to_db(self):
        """
        Make all entities
        """
        # Create sequencing_center
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()

        # Data
        kwargs = {
            'experiment_strategy': 'WXS',
            'library_name': 'library',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'platform',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        # Create many to many se and gf
        ses = []
        gfs = []
        for i in range(2):
            gfs.append(
                GenomicFile(external_id='gf{}'.format(i))
            )
            ses.append(
                SequencingExperiment(**kwargs,
                                     sequencing_center=sc,
                                     external_id='se{}'.format(i))
            )
        db.session.add(SequencingExperimentGenomicFile(
            genomic_file=gfs[0],
            sequencing_experiment=ses[0],
            external_id='se0-gf0'))
        db.session.add(SequencingExperimentGenomicFile(
            genomic_file=gfs[0],
            sequencing_experiment=ses[1],
            external_id='se1-gf0'))
        db.session.add(SequencingExperimentGenomicFile(
            genomic_file=gfs[1],
            sequencing_experiment=ses[0],
            external_id='se0-gf1'))
        db.session.add(SequencingExperimentGenomicFile(
            genomic_file=gfs[1],
            sequencing_experiment=ses[1],
            external_id='se1-gf1'))

        db.session.commit()

        return ses, gfs
