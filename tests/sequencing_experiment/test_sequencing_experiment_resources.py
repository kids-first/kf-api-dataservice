import json
from flask import url_for
from datetime import datetime
from urllib.parse import urlparse
from dateutil import parser, tz

from dataservice.extensions import db
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.sample.models import Sample
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
        kwargs = {
            'external_id': 'se1',
            'experiment_date': str(kwargs.get('experiment_date')),
            'experiment_strategy': 'WGS',
            'center': 'Baylor',
            'library_name': 'a library',
            'library_strand': 'a strand',
            'is_paired_end': True,
            'platform': 'Illumina',
            'instrument_model': 'HiSeqX',
            'max_insert_size': 500,
            'mean_insert_size': 300,
            'mean_depth': 60.89,
            'total_reads': 1000,
            'mean_read_length': 50,
            'aliquot_id': kwargs.get('aliquot_id')
        }
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
            if k is 'aliquot_id':
                continue
            if k is 'experiment_date':
                self.assertEqual(parser.parse(sequencing_experiment[k]),
                                 parser.parse(v))
            else:
                self.assertEqual(sequencing_experiment[k], v)

        self.assertEqual(2, SequencingExperiment.query.count())

    def test_post_multiple(self):
        # Create a sequencing_experiment with participant
        se1 = self._create_save_to_db()

        # Create another sequencing_experiment for the same participant
        # Create sequencing_experiment data
        se2 = {
            'external_id': 'se2',
            'experiment_date': str(se1.get('experiment_date')),
            'experiment_strategy': 'WGS',
            'center': 'Baylor',
            'library_name': 'a library',
            'library_strand': 'a strand',
            'is_paired_end': True,
            'platform': 'Illumina',
            'instrument_model': 'HiSeqX',
            'max_insert_size': 500,
            'mean_insert_size': 300,
            'mean_depth': 60.89,
            'total_reads': 1000,
            'mean_read_length': 50,
            'aliquot_id': se1.get('aliquot_id')
        }
        # Send post request
        response = self.client.post(url_for(SEQUENCING_EXPERIMENTS_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(se2))
        # Check status code
        self.assertEqual(response.status_code, 201)
        # Check database
        self.assertEqual(2, SequencingExperiment.query.count())
        sequencing_experiments = Aliquot.query.all()[0].sequencing_experiments
        self.assertEqual(2, len(sequencing_experiments))

    def test_get(self):
        """
        Test retrieval of sequencing_experiment and check link to aliquot
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
        aliquot_link = response['_links']['aliquot']
        sample_id = urlparse(aliquot_link).path.split('/')[-1]
        for k, v in kwargs.items():
            if k == 'aliquot_id':
                self.assertEqual(sample_id,
                                 kwargs['aliquot_id'])
            else:
                if isinstance(v, datetime):
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
            'center': 'Baylor',
            'library_name': 'a library',
            'library_strand': 'a strand',
            'is_paired_end': True,
            'platform': 'Illumina',
            'instrument_model': 'HiSeqX',
            'aliquot_id': kwargs.get('aliquot_id')
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

        Requires creating a participant, and sample
        """
        # Create study
        st = Study(external_id='phs001')
        # Create sample
        sa = Sample(external_id='sa0')
        # Create aliquot
        al = Aliquot(external_id='al0', analyte_type='DNA')

        dt = datetime.now()
        kwargs = {
            'external_id': 'se',
            'experiment_date': dt.replace(tzinfo=tz.tzutc()),
            'experiment_strategy': 'WGS',
            'center': 'Broad Institute',
            'library_name': 'a library',
            'library_strand': 'a strand',
            'is_paired_end': True,
            'platform': 'Illumina',
            'instrument_model': 'HiSeqX',
            'max_insert_size': 500,
            'mean_insert_size': 300,
            'mean_depth': 60.89,
            'total_reads': 1000,
            'mean_read_length': 50
        }
        se = SequencingExperiment(**kwargs)

        # Create and save participant, sample, aliquot, sequencing_experiment
        al.sequencing_experiments.append(se)
        sa.aliquots.append(al)
        pt = Participant(external_id='P0',
                         samples=[sa],
                         is_proband=True)
        st.participants.append(pt)
        db.session.add(st)
        db.session.commit()

        kwargs['aliquot_id'] = al.kf_id
        kwargs['kf_id'] = se.kf_id

        return kwargs
