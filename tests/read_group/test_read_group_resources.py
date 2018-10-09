import json
from datetime import datetime

from flask import url_for
from dateutil import parser, tz

from dataservice.extensions import db
from dataservice.api.read_group.models import ReadGroup
from tests.utils import FlaskTestCase

READ_GROUPS_URL = 'api.read_groups'
READ_GROUPS_LIST_URL = 'api.read_groups_list'


class ReadGroupTest(FlaskTestCase):
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
