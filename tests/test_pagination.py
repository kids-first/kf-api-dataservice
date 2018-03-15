import json
import pytest
from dateutil import parser

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.demographic.models import Demographic
from dataservice.api.sample.models import Sample
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.study.models import Study


class TestPagination:
    """
    Test that entities are iterated and returned properly
    """

    @pytest.fixture(scope='function')
    def participants(client):
        s = Study(external_id='blah', name='test')
        db.session.add(s)
        db.session.flush()
        for i in range(102):
            p = Participant(external_id="test",
                            study_id=s.kf_id,
                            is_proband=True)
            d = Demographic(race='cat')
            p.demographic = d
            samp = Sample()
            p.samples = [samp]
            diag = Diagnosis()
            p.diagnoses = [diag]
            db.session.add(p)
        db.session.commit()

    @pytest.mark.parametrize('endpoint', [
        ('/participants'),
        ('/demographics'),
        ('/samples'),
        ('/diagnoses'),
    ])
    def test_pagination(self, client, participants, endpoint):
        """ Test pagination of resource """
        resp = client.get(endpoint)
        resp = json.loads(resp.data.decode('utf-8'))
        
        assert len(resp['results']) == 10
        assert resp['limit'] == 10
        assert resp['total'] == 102

        ids_seen = []
        # Iterate through via the `next` link
        while 'next' in resp['_links']:
            # Check formatting of next link
            assert float(resp['_links']['next'].split('=')[-1])
            # Stash all the ids on the page
            ids_seen.extend([r['kf_id'] for r in resp['results']])
            resp = client.get(resp['_links']['next'])
            resp = json.loads(resp.data.decode('utf-8'))
            # Check formatting of the self link
            assert float(resp['_links']['self'].split('=')[-1])

        ids_seen.extend([r['kf_id'] for r in resp['results']])

        assert len(ids_seen) == resp['total']

    @pytest.mark.parametrize('endpoint', [
        ('/participants'),
        ('/demographics'),
        ('/samples'),
        ('/diagnoses'),
    ])
    def test_limit(self, client, participants, endpoint):
        # Check that limit param operates correctly
        response = client.get(endpoint+'?limit=5')
        response = json.loads(response.data.decode('utf-8'))
        assert len(response['results']) == 5
        assert response['limit'] == 5

        response = client.get(endpoint+'?limit=200')
        response = json.loads(response.data.decode('utf-8'))
        assert len(response['results']) == 100

        # Check unexpected limit param uses default
        response = client.get(endpoint+'?limit=dog')
        response =  json.loads(response.data.decode('utf-8'))
        assert len(response['results']) == 10
        assert response['limit'] == 10

    @pytest.mark.parametrize('endpoint', [
        ('/participants'),
        ('/demographics'),
        ('/samples'),
        ('/diagnoses'),
    ])
    def test_after(self, client, participants, endpoint):
        """ Test `after` offeset paramater """
        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        first = response['results'][0]['created_at']

        # Check unexpected after param returns the earliest
        response = client.get(endpoint+'?after=dog')
        response = json.loads(response.data.decode('utf-8'))
        assert response['results'][0]['created_at'] == first
        assert response['_links']['self'] == endpoint


        # Check that future dates return no results
        response = client.get(endpoint+'?after=2100-01-01')
        response = json.loads(response.data.decode('utf-8'))
        assert response['results'] == []

        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        ts = parser.parse(response['results'][-1]['created_at']).timestamp()

    @pytest.mark.parametrize('endpoint', [
        ('/participants'),
        ('/demographics'),
        ('/samples'),
        ('/diagnoses'),
    ])
    def test_self(self, client, participants, endpoint):
        """ Test that the self link gives the same page """
        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        next_page = response['_links']['next']

        response = client.get(next_page)
        response = json.loads(response.data.decode('utf-8'))
        results = response['results']

        response = client.get(response['_links']['self'])
        response = json.loads(response.data.decode('utf-8'))
        assert results == response['results']

    @pytest.mark.parametrize('endpoint', [
        ('/participants'),
        ('/demographics'),
        ('/samples'),
        ('/diagnoses'),
    ])
    def test_individual_links(self, client, participants, endpoint):
        """ Test that each individual result has properly formatted _links """
        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        results = response['results']

        for result in results:
            assert '_links' in result
            self_link = result['_links']
            response = client.get(result['_links']['self'])
            assert response.status_code  == 200
            response = json.loads(response.data.decode('utf-8'))
            assert response['_status']['code'] == 200
            # Should only return the single entity
            assert isinstance(response['results'], dict)
            assert result['kf_id'] == response['results']['kf_id']
            assert 'collection' in result['_links']
