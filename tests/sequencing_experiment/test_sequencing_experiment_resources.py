import json
from datetime import datetime
from dateutil import parser, tz
from urllib.parse import urlencode

from flask import url_for

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.sequencing_experiment.models import (
    SequencingExperiment,
    SequencingExperimentGenomicFile
)
from tests.utils import IndexdTestCase

SEQUENCING_EXPERIMENTS_URL = 'api.sequencing_experiments'
SEQUENCING_EXPERIMENTS_LIST_URL = 'api.sequencing_experiments_list'


class SequencingExperimentTest(IndexdTestCase):
    """
    Test sequencing_experiment api
    """

    def test_post(self):
        """
        Test create a new sequencing_experiment
        """
        sc = SequencingCenter(name='sc')
        db.session.add(sc)
        db.session.commit()

        kwargs = {
            'external_id': 'blah',
            'experiment_strategy': 'WXS',
            'library_name': 'Test_library_name_1',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'Illumina',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200,
            'sequencing_center_id': sc.kf_id
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
            if 'sequencing_center_id':
                continue
            self.assertEqual(sequencing_experiment[k], v)

        self.assertEqual(1, SequencingExperiment.query.count())

    def test_get(self):
        """
        Test retrieval of sequencing_experiment
        """
        # Create and save sequencing_experiment to db
        se = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(SEQUENCING_EXPERIMENTS_URL,
                                           kf_id=se.kf_id),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        sequencing_experiment = response['results']
        for k, v in sequencing_experiment.items():
            attr = getattr(se, k)
            if isinstance(attr, datetime):
                attr = attr.replace(tzinfo=tz.tzutc()).isoformat()
            self.assertEqual(sequencing_experiment[k], attr)

    def test_filter_by_gf(self):
        """
        Test get and filter seq exps by study_id and/or genomic_file_id
        """
        ses, gfs, studies = self._create_all_entities()

        # Create query
        gf = GenomicFile.query.filter_by(external_id='study0-gf1').first()
        segfs = SequencingExperimentGenomicFile.query.filter_by(
            genomic_file_id=gf.kf_id).all()
        assert len(segfs) == 1
        assert segfs[0].sequencing_experiment.external_id == 'study0-se0'

        # Send get request
        filter_params = {'genomic_file_id': gf.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/sequencing-experiments', qs)
        response = self.client.get(endpoint, headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 1 == response['total']
        assert 1 == len(response['results'])
        sequencing_experiment = response['results'][0]
        assert sequencing_experiment['external_id'] == 'study0-se0'

    def test_patch(self):
        """
        Test partial update of an existing sequencing_experiment
        """
        se = self._create_save_to_db()
        kf_id = se.kf_id

        # Update existing sequencing_experiment
        body = {'external_id': 'updated'}

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

        # Check counts
        self.assertEqual(1, SequencingExperiment.query.count())

    def test_delete(self):
        """
        Test delete an existing sequencing_experiment
        """
        se = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(SEQUENCING_EXPERIMENTS_URL,
                                              kf_id=se.kf_id),
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
        sc = SequencingCenter(name='sc')
        kwargs = {
            'external_id': 'blah',
            'experiment_strategy': 'WXS',
            'library_name': 'Test_library_name_1',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'Illumina',
            'instrument_model': '454 GS FLX Titanium',
            'max_insert_size': 600,
            'mean_insert_size': 500,
            'mean_depth': 40,
            'total_reads': 800,
            'mean_read_length': 200
        }
        se = SequencingExperiment(**kwargs, sequencing_center=sc)

        db.session.add(se)
        db.session.commit()

        return se

    def _create_all_entities(self):
        """
        Create 2 studies with genomic files and read groups
        """
        sc = SequencingCenter(name='sc')
        studies = []
        ses = {}
        gfs = {}
        for j in range(2):
            s = Study(external_id='s{}'.format(j))
            p = Participant(external_id='p{}'.format(j))
            s.participants.append(p)
            study_gfs = gfs.setdefault('study{}'.format(j), [])
            for i in range(3):
                b = Biospecimen(external_sample_id='b{}'.format(i),
                                analyte_type='DNA',
                                sequencing_center=sc,
                                participant=p)
                gf = GenomicFile(
                    external_id='study{}-gf{}'.format(j, i),
                    urls=['s3://mybucket/key'],
                    hashes={'md5': 'd418219b883fce3a085b1b7f38b01e37'})
                study_gfs.append(gf)
                b.genomic_files.append(gf)

            study_ses = ses.setdefault('study{}'.format(j), [])
            dt = datetime.now()
            kwargs = {
                'experiment_date': str(dt.replace(tzinfo=tz.tzutc())),
                'experiment_strategy': 'WXS',
                'library_name': 'Test_library_name_1',
                'library_strand': 'Unstranded',
                'is_paired_end': False,
                'platform': 'Illumina',
                'instrument_model': '454 GS FLX Titanium',
                'max_insert_size': 600,
                'mean_insert_size': 500,
                'mean_depth': 40,
                'total_reads': 800,
                'mean_read_length': 200
            }
            se0 = SequencingExperiment(**kwargs,
                                       sequencing_center=sc,
                                       external_id='study{}-se0'.format(j))
            se0.genomic_files.extend(study_gfs[0:2])
            se1 = SequencingExperiment(**kwargs,
                                       sequencing_center=sc,
                                       external_id='study{}-se1'.format(j))
            se1.genomic_files.extend([study_gfs[0],
                                      study_gfs[-1]])

            study_ses.extend([se0, se1])
            studies.append(s)

        db.session.add_all(studies)
        db.session.commit()

        return ses, gfs, studies
