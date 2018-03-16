import json
from flask import url_for
from datetime import datetime
from urllib.parse import urlparse
from dateutil import parser, tz

from dataservice.extensions import db
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.sample.models import Sample
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

ALIQUOTS_URL = 'api.aliquots'
ALIQUOTS_LIST_URL = 'api.aliquots_list'


class AliquotTest(FlaskTestCase):
    """
    Test aliquot api
    """

    def test_post(self):
        """
        Test create a new aliquot
        """
        kwargs = self._create_save_to_db()

        # Create aliquot data
        dt = datetime.now()
        kwargs = {
            'external_id': 'AL1',
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Baylor',
            'analyte_type': 'DNA',
            'concentration': 200,
            'volume': 13.99,
            'shipment_date': str(dt.replace(tzinfo=tz.tzutc())),
            'sample_id': kwargs.get('sample_id')
        }
        # Send get request
        response = self.client.post(url_for(ALIQUOTS_LIST_URL),
                                    data=json.dumps(kwargs),
                                    headers=self._api_headers())

        # Check response status status_code
        self.assertEqual(response.status_code, 201)

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        aliquot = response['results']
        for k, v in kwargs.items():
            if k is 'sample_id':
                continue
            if k is 'shipment_date':
                self.assertEqual(parser.parse(aliquot[k]), parser.parse(v))
            else:
                self.assertEqual(aliquot[k], v)

        self.assertEqual(2, Aliquot.query.count())

    def test_post_multiple(self):
        # Create a aliquot with participant
        a1 = self._create_save_to_db()

        # Create another aliquot for the same participant
        a2 = {
            'external_id': 'AL1',
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Baylor',
            'analyte_type': 'DNA',
            'concentration': 200,
            'volume': 13.99,
            'sample_id': a1.get('sample_id')
        }
        # Send post request
        response = self.client.post(url_for(ALIQUOTS_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(a2))
        # Check status code
        self.assertEqual(response.status_code, 201)
        # Check database
        self.assertEqual(2, Aliquot.query.count())
        aliquots = Sample.query.all()[0].aliquots
        self.assertEqual(2, len(aliquots))

    def test_get(self):
        """
        Test retrieval of aliquot and check link to sample
        """
        # Create and save aliquot to db
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.get(url_for(ALIQUOTS_URL,
                                           kf_id=kwargs['kf_id']),
                                   headers=self._api_headers())

        # Check response status code
        self.assertEqual(response.status_code, 200)
        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        aliquot = response['results']
        sample_link = response['_links']['sample']
        sample_id = urlparse(sample_link).path.split('/')[-1]
        for k, v in kwargs.items():
            if k == 'sample_id':
                self.assertEqual(sample_id,
                                 kwargs['sample_id'])
            else:
                if isinstance(v, datetime):
                    d = v.replace(tzinfo=tz.tzutc())
                    self.assertEqual(str(parser.parse(aliquot[k])), str(d))
                else:
                    self.assertEqual(aliquot[k], kwargs[k])

    def test_patch(self):
        """
        Test partial update of an existing aliquot
        """
        kwargs = self._create_save_to_db()
        kf_id = kwargs.get('kf_id')

        # Update existing aliquot
        body = {
            'concentration': 0,
            'volume': 0
        }
        response = self.client.patch(url_for(ALIQUOTS_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        # Status code
        self.assertEqual(response.status_code, 200)

        # Message
        resp = json.loads(response.data.decode("utf-8"))
        self.assertIn('aliquot', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        # Content - check only patched fields are updated
        aliquot = resp['results']
        al = Aliquot.query.get(kf_id)
        for k, v in body.items():
            self.assertEqual(v, getattr(al, k))
        # Content - Check remaining fields are unchanged
        unchanged_keys = (set(aliquot.keys()) -
                          set(body.keys()))
        for k in unchanged_keys:
            val = getattr(al, k)
            if isinstance(val, datetime):
                d = val.replace(tzinfo=tz.tzutc())
                self.assertEqual(str(parser.parse(aliquot[k])), str(d))
            else:
                self.assertEqual(aliquot[k], val)

        self.assertEqual(1, Aliquot.query.count())

    def test_delete(self):
        """
        Test delete an existing aliquot
        """
        kwargs = self._create_save_to_db()
        # Send get request
        response = self.client.delete(url_for(ALIQUOTS_URL,
                                              kf_id=kwargs['kf_id']),
                                      headers=self._api_headers())
        # Check status code
        self.assertEqual(response.status_code, 200)
        # Check response body
        response = json.loads(response.data.decode("utf-8"))
        # Check database
        d = Aliquot.query.first()
        self.assertIs(d, None)

    def _create_save_to_db(self):
        """
        Create and save aliquot

        Requires creating a participant, and sample
        """
        # Create study
        st = Study(external_id='phs001')

        # Create sample
        kwargs = {
            'external_id': 's1',
            'tissue_type': 'Normal',
            'composition': 'composition1',
            'anatomical_site': 'Brain',
            'age_at_event_days': 365,
            'tumor_descriptor': 'Metastatic',
        }
        sa = Sample(**kwargs)

        # Create aliquot
        dt = datetime.now()
        kwargs = {
            'external_id': 'AL0',
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Broad Institute',
            'analyte_type': 'DNA',
            'concentration': 100,
            'volume': 12.67,
            'shipment_date': dt
        }
        al = Aliquot(**kwargs)

        # Create and save participant, sample, aliquot
        sa.aliquots.append(al)
        pt = Participant(external_id='P0',
                         samples=[sa],
                         is_proband=True)
        st.participants.append(pt)
        db.session.add(st)
        db.session.commit()

        kwargs['sample_id'] = sa.kf_id
        kwargs['kf_id'] = al.kf_id

        return kwargs
