import json
from datetime import datetime

from flask import url_for
from dateutil import parser, tz

from dataservice.extensions import db
from dataservice.api.read_group.models import (
    ReadGroup,
    ReadGroupGenomicFile
)
from dataservice.api.genomic_file.models import GenomicFile
from tests.utils import IndexdTestCase

RG_GF_URL = 'api.read_group_genomic_files'
RG_GF_LIST_URL = 'api.read_group_genomic_files_list'


class ReadGroupGenomicFileTest(IndexdTestCase):
    """
    Test read_group_genomic_file api
    """

    def test_post(self):
        """
        Test create a new read_group_genomic_file
        """
        # Create needed entities
        gf = GenomicFile(external_id='gf0')
        rg = ReadGroup(external_id='rg0')
        db.session.add_all([gf, rg])
        db.session.commit()

        kwargs = {'read_group_id': rg.kf_id,
                  'genomic_file_id': gf.kf_id,
                  'external_id': 'rg0-gf0'
                  }

        # Send get request
        response = self.client.post(url_for(RG_GF_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        assert response['results']['kf_id']
        self.assertEqual(1, ReadGroupGenomicFile.query.count())

    def test_get(self):
        """
        Test retrieval of read_group_genomic_file
        """
        # Create and save read_group to db
        rgs, rgs = self._create_save_to_db()
        rgf = ReadGroupGenomicFile.query.first()
        # Send get request
        response = self.client.get(url_for(RG_GF_URL,
                                           kf_id=rgf.kf_id),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        read_group_gf = response['results']
        for k, v in read_group_gf.items():
            attr = getattr(rgf, k)
            if isinstance(attr, datetime):
                attr = attr.replace(tzinfo=tz.tzutc()).isoformat()
            self.assertEqual(read_group_gf[k], attr)

    def test_patch(self):
        """
        Test partial update of an existing read_group_genomic_file
        """
        rgs, gfs = self._create_save_to_db()
        rgf = ReadGroupGenomicFile.query.first()

        # Update existing read_group
        body = {'external_id': 'updated'}

        response = self.client.patch(url_for(RG_GF_URL,
                                             kf_id=rgf.kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('read_group', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        read_group_gf = resp['results']
        for k, v in body.items():
            self.assertEqual(v, getattr(rgf, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(read_group_gf.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(rgf, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(
                    str(parser.parse(read_group_gf[k])), str(d))
            else:
                self.assertEqual(read_group_gf[k], val)

        # Check counts
        self.assertEqual(4, ReadGroupGenomicFile.query.count())

    def test_delete(self):
        """
        Test delete an existing read_group_genomic_file
        """
        rgs, gfs = self._create_save_to_db()
        kf_id = ReadGroupGenomicFile.query.first().kf_id

        # Send get request
        response = self.client.delete(url_for(RG_GF_URL,
                                              kf_id=kf_id),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        rgf = ReadGroupGenomicFile.query.get(kf_id)
        self.assertIs(rgf, None)

    def _create_save_to_db(self):
        """
        Make all entities
        """
        # Create many to many rg and gf
        rgs = []
        gfs = []
        for i in range(2):
            gfs.append(
                GenomicFile(external_id='gf{}'.format(i))
            )
            rgs.append(
                ReadGroup(external_id='rg{}'.format(i))
            )
        db.session.add(ReadGroupGenomicFile(genomic_file=gfs[0],
                                            read_group=rgs[0],
                                            external_id='rg0-gf0'))
        db.session.add(ReadGroupGenomicFile(genomic_file=gfs[0],
                                            read_group=rgs[1],
                                            external_id='rg1-gf0'))
        db.session.add(ReadGroupGenomicFile(genomic_file=gfs[1],
                                            read_group=rgs[0],
                                            external_id='rg0-gf1'))
        db.session.add(ReadGroupGenomicFile(genomic_file=gfs[1],
                                            read_group=rgs[1],
                                            external_id='rg1-gf1'))

        db.session.commit()

        return rgs, gfs
