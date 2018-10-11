import json
from datetime import datetime

from flask import url_for
from dateutil import parser, tz
from urllib.parse import urlencode

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.read_group.models import ReadGroup, ReadGroupGenomicFile
from tests.utils import IndexdTestCase

READ_GROUPS_URL = 'api.read_groups'
READ_GROUPS_LIST_URL = 'api.read_groups_list'


class ReadGroupTest(IndexdTestCase):
    """
    Test read_group api
    """

    def test_post(self):
        """
        Test create a new read_group
        """
        kwargs = {'external_id': 'blah',
                  'lane_number': 3,
                  'flow_cell': 'FL0101'
                  }

        # Send get request
        response = self.client.post(url_for(READ_GROUPS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        read_group = response['results']
        for k, v in kwargs.items():
            self.assertEqual(read_group[k], v)

        self.assertEqual(1, ReadGroup.query.count())

    def test_get(self):
        """
        Test retrieval of read_group
        """
        # Create and save read_group to db
        rg = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(READ_GROUPS_URL,
                                           kf_id=rg.kf_id),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        read_group = response['results']
        for k, v in read_group.items():
            attr = getattr(rg, k)
            if isinstance(attr, datetime):
                attr = attr.replace(tzinfo=tz.tzutc()).isoformat()
            self.assertEqual(read_group[k], attr)

    def test_filter_by_gf(self):
        """
        Test get and filter read groups by study_id and/or genomic_file_id
        """
        rgs, gfs, studies = self._create_all_entities()

        # Create query
        gf = GenomicFile.query.filter_by(external_id='study0-gf1').first()
        rgfs = ReadGroupGenomicFile.query.filter_by(
            genomic_file_id=gf.kf_id).all()
        assert len(rgfs) == 1
        assert rgfs[0].read_group.external_id == 'study0-rg0'

        # Send get request
        filter_params = {'genomic_file_id': gf.kf_id}
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format('/read-groups', qs)
        response = self.client.get(endpoint, headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert 1 == response['total']
        assert 1 == len(response['results'])
        read_group = response['results'][0]
        assert read_group['external_id'] == 'study0-rg0'

    def test_patch(self):
        """
        Test partial update of an existing read_group
        """
        rg = self._create_save_to_db()
        kf_id = rg.kf_id

        # Update existing read_group
        body = {'external_id': 'updated'}

        response = self.client.patch(url_for(READ_GROUPS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('read_group', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        read_group = resp['results']
        rg = ReadGroup.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(rg, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(read_group.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(rg, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(
                    str(parser.parse(read_group[k])), str(d))
            else:
                self.assertEqual(read_group[k], val)

        # Check counts
        self.assertEqual(1, ReadGroup.query.count())

    def test_delete(self):
        """
        Test delete an existing read_group
        """
        rg = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(READ_GROUPS_URL,
                                              kf_id=rg.kf_id),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        rg = ReadGroup.query.first()
        self.assertIs(rg, None)

    def _create_save_to_db(self):
        """
        Create and save read_group
        """
        rg = ReadGroup(external_id='blah',
                       lane_number=3,
                       flow_cell='FL0101')

        db.session.add(rg)
        db.session.commit()

        return rg

    def _create_all_entities(self):
        """
        Create 2 studies with genomic files and read groups
        """
        sc = SequencingCenter(name='sc')
        studies = []
        rgs = {}
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

            study_rgs = rgs.setdefault('study{}'.format(j), [])

            rg0 = ReadGroup(external_id='study{}-rg0'.format(j))
            rg0.genomic_files.extend(study_gfs[0:2])
            rg1 = ReadGroup(external_id='study{}-rg1'.format(j))
            rg1.genomic_files.extend([study_gfs[0],
                                      study_gfs[-1]])

            study_rgs.extend([rg0, rg1])
            studies.append(s)

        db.session.add_all(studies)
        db.session.commit()

        return rgs, gfs, studies
