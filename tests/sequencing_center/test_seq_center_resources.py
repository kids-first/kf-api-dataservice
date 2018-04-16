import json
from flask import url_for
from datetime import datetime
from urllib.parse import urlparse
from dateutil import parser, tz

from dataservice.extensions import db
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from tests.utils import FlaskTestCase

SEQUENCING_CENTERS_URL = 'api.sequencing_centers'
SEQUENCING_CENTERS_LIST_URL = 'api.sequencing_centers_list'


class SequencingCenterTest(FlaskTestCase):
    """
    Test sequencing_center api
    """

    def test_post(self):
        """
        Test create a new sequencing_center
        """
        seq_data = self._make_seq_exp(external_id='se')
        se = SequencingExperiment(**seq_data)
        db.session.add(se)
        db.session.commit()
        # Create sequencing_center data
        kwargs ={
                'name': "Baylor",
                'sequencing_experiment_id': se.kf_id
        }
        # Send get request
        response = self.client.post(url_for(SEQUENCING_CENTERS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sequencing_center = response['results']

        self.assertEqual(sequencing_center['name'], kwargs['name'])
        self.assertEqual(1, SequencingCenter.query.count())

    def test_get(self):
        """
        Test retrieval of sequencing_experiment
        """
        # Create and save sequencing_center to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(SEQUENCING_CENTERS_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sequencing_center = response['results']
        self.assertEqual(sequencing_center['name'], kwargs['name'])

    def test_patch(self):
        """
        Test partial update of an existing sequencing_center
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')

        # Update existing sequencing_center
        body = {
            'name': 'updated_name',
        }
        response = self.client.patch(url_for(SEQUENCING_CENTERS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('sequencing_center', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        sequencing_center = resp['results']
        se = SequencingCenter.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(se, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(sequencing_center.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(se, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(
                    str(parser.parse(sequencing_center[k])), str(d))
            else:
                self.assertEqual(sequencing_center[k], val)
        self.assertEqual(1, SequencingCenter.query.count())

    def test_delete(self):
        """
        Test delete an existing sequencing_experiment
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(SEQUENCING_CENTERS_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        self.assertEqual(0, SequencingCenter.query.count())

    def _create_save_to_db(self):
        """
        Create and save sequencing_center
        """

        seq_data = self._make_seq_exp(external_id='se')
        se = SequencingExperiment(**seq_data)
        db.session.add(se)
        db.session.commit()
        kwargs ={
                'name': "Baylor",
                'sequencing_experiment_id': se.kf_id
        }
        sc = SequencingCenter(**kwargs)
        db.session.add(sc)
        db.session.commit()
        kwargs['kf_id'] = sc.kf_id
        return kwargs

    def _make_seq_exp(self, external_id=None):
        '''
        Convenience method to create a sequencing experiment with a
        given source name
        .replace(tzinfo=tz.tzutc())
        '''
        dt = datetime.now()
        seq_experiment_data = {
            'external_id':external_id,
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
