import json
from flask import url_for
from datetime import datetime
from urllib.parse import urlparse
from dateutil import parser, tz

from dataservice.extensions import db
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

SEQUENCING_EXPERIMENTS_URL = 'api.sequencing_experiments'
SEQUENCING_EXPERIMENTS_LIST_URL = 'api.sequencing_experiments_list'


class SequencingExperimentTest(FlaskTestCase):
    """
    Test sequencing_experiment api
    """

    def test_post(self):
        """
        Test create a new sequencing_experiment
        """
        kwargs = self._create_save_to_db()

        # Create sequencing_experiment data
        kwargs = self._make_seq_exp(external_id='se1')
        sc = SequencingCenter.query.first()
        kwargs['sequencing_center_id'] = sc.kf_id
        # Send get request
        response = self.client.post(url_for(SEQUENCING_EXPERIMENTS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sequencing_experiment = response['results']
        for k, v in kwargs.items():
            if k is 'sequencing_center_id':
                continue
            if k is 'experiment_date':
                self.assertEqual(parser.parse(sequencing_experiment[k]),
                                 parser.parse(v))
            else:
                self.assertEqual(sequencing_experiment[k], v)

        self.assertEqual(2, SequencingExperiment.query.count())

        # Check for allow none fields
        kwargs['experiment_date'] = None
        # Send get request
        response = self.client.post(url_for(SEQUENCING_EXPERIMENTS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())
        # Check response status status_code
        self.assertEqual(response.status_code, 201)
        response = json.loads(response.data.decode('utf-8'))
        self.assertIs(response['results']['experiment_date'], None)
        self.assertEqual(3, SequencingExperiment.query.count())

    def test_get(self):
        """
        Test retrieval of sequencing_experiment
        """
        # Create and save sequencing_experiment to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(SEQUENCING_EXPERIMENTS_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sequencing_experiment = response['results']
        for k, v in kwargs.items():
            if k is 'sequencing_center_id':
                continue
            if k is 'experiment_date':
                self.assertEqual(
                    str(parser.parse(sequencing_experiment[k])), str(v))
            else:
                self.assertEqual(sequencing_experiment[k], kwargs[k])

    def test_patch(self):
        """
        Test partial update of an existing sequencing_experiment
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')

        # Update existing sequencing_experiment
        body = {
            'external_id': 'se2',
            'experiment_strategy': 'WGS',
            'library_name': 'a library',
            'library_strand': 'a strand',
            'is_paired_end': True,
            'platform': 'Illumina',
            'instrument_model': 'HiSeqX'
        }
        response = self.client.patch(url_for(SEQUENCING_EXPERIMENTS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('sequencing_experiment', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        sequencing_experiment = resp['results']
        se = SequencingExperiment.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(se, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(sequencing_experiment.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(se, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(
                    str(parser.parse(sequencing_experiment[k])), str(d))
            else:
                self.assertEqual(sequencing_experiment[k], val)
        self.assertEqual(1, SequencingExperiment.query.count())

    def test_delete(self):
        """
        Test delete an existing sequencing_experiment
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(SEQUENCING_EXPERIMENTS_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        se = SequencingExperiment.query.first()
        self.assertIs(se, None)

    def _create_save_to_db(self):
        """
        Create and save sequencing_experiment
        """
        sc = SequencingCenter(name="Baylor")
        kwargs = self._make_seq_exp(external_id='se')
        se = SequencingExperiment(**kwargs,
                                  sequencing_center_id=sc.kf_id)
        sc.sequencing_experiments.extend([se])
        db.session.add(sc)
        db.session.commit()
        kwargs['kf_id'] = se.kf_id
        kwargs['sequencing_center_id'] = sc.kf_id

        return kwargs

    def _make_seq_exp(self, external_id=None):
        '''
        Convenience method to create a sequencing experiment with a
        given source name
        '''
        dt = datetime.now()
        seq_experiment_data = {
            'external_id': external_id,
            'experiment_date': str(dt.replace(tzinfo=tz.tzutc())),
            'experiment_strategy': 'WXS',
            'library_name': 'Test_library_name_1',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'Test_platform_name_1',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        return seq_experiment_data
