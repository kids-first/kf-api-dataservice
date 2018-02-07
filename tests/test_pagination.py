import json
import pytest

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study


class TestPagination:
    """
    """


    @pytest.fixture
    def participants(client):
        s = Study(external_id='blah', name='test')
        db.session.add(s)
        db.session.flush()
        for i in range(102):
            p = Participant(external_id="test", study_id=s.kf_id)
            db.session.add(p)
        db.session.commit()

    @pytest.mark.parametrize('endpoint', [
        ('/participants'),
    ])
    def test_pagination(self, client, participants, endpoint):
        """ Test pagination of resource """
        response = client.get(endpoint)
        response =  json.loads(response.data)
        
        assert len(response['results']) == 10
        assert response['limit'] == 10
        assert response['total'] == 102

        # Check that limit param operates correctly
        response = client.get(endpoint+'?limit=5')
        response =  json.loads(response.data)
        assert len(response['results']) == 5
        assert response['limit'] == 5

        response = client.get(endpoint+'?limit=200')
        response =  json.loads(response.data)
        assert len(response['results']) == 100

        # Check unexpected limit param uses default
        response = client.get(endpoint+'?limit=dog')
        response =  json.loads(response.data)
        assert len(response['results']) == 10
        assert response['limit'] == 10

        # Check that page param operates correctly
        response = client.get(endpoint)
        response =  json.loads(response.data)
        assert response['page'] == 1

        response = client.get(endpoint+'?page=5')
        response =  json.loads(response.data)
        assert response['page'] == 5
        assert response['_links']['next'].endswith('?page=6')
        assert response['_links']['prev'].endswith('?page=4')
        assert response['_links']['self'].endswith('?page=5')

        # Check unexpected page param returns page 1 
        response = client.get(endpoint+'?page=dog')
        response =  json.loads(response.data)
        assert response['_links']['self'].endswith('?page=1')

        response = client.get(endpoint+'?limit=2')
        response =  json.loads(response.data)

        # Check unexpected page param returns page 1 
        response = client.get(endpoint+'?page=1000')
        assert response.status_code == 404
        response =  json.loads(response.data)
        assert response['_status']['code'] == 404
