import pytest
import json
from dateutil import parser, tz
from urllib.parse import urlencode

from tests.conftest import (
    ENTITY_ENDPOINT_MAP,
    ENDPOINTS,
    ENTITY_PARAMS
)


class TestFilterParams:
    """
    Test filtering on pagnation endpoints
    """

    @pytest.mark.parametrize('model',
                             [
                                 (model)
                                 for model in ENTITY_ENDPOINT_MAP.keys()
                             ])
    def test_filter_params(self, client, entities, model):
        """
        Test retrieving entities given filter parameters
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]
        filter_params = ENTITY_PARAMS['filter_params'][endpoint]['valid']
        expected_total = model.query.filter_by(
            **filter_params).count()

        # Make query string
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 200
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert resp['limit'] == 10
        assert len(resp['results']) == min(expected_total, 10)
        assert resp['total'] == expected_total
        # All results have correct field values
        for result in resp['results']:
            for k, v in filter_params.items():
                if k.lower().endswith('date'):
                    v = 'T'.join(v.split(' '))
                assert result.get(k) == v

    @pytest.mark.parametrize('endpoint, invalid_params',
                             [(endpoint, invalid_param)
                              for endpoint in ENDPOINTS
                                 for invalid_param in ENTITY_PARAMS.get(
                                 'filter_params')[endpoint]['invalid']
                              ])
    def test_invalid_filter_params(self, client, entities, endpoint,
                                   invalid_params):
        """
        Test retrieving entities given invalid filter parameters
        """
        # Make query string
        qs = urlencode(invalid_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 400
        # Check content
        resp = json.loads(response.data.decode('utf-8'))

        assert ('could not retrieve entities:' in
                resp['_status']['message'])
        for k, v in invalid_params.items():
            assert k in resp['_status']['message']

    @pytest.mark.parametrize('model',
                             [
                                 (model)
                                 for model in ENTITY_ENDPOINT_MAP.keys()
                             ])
    def test_unknown_filter_params(self, client, entities, model):
        """
        Test retrieving entities given filter parameters that don't exist on
        the entity
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]
        if model.__name__ == 'Study':
            filter_params = {'study_id': 'SD_00001111'}
        else:
            filter_params = {'blabbityboo': 'foo'}

        expected_total = model.query.count()

        # Make query string
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 200
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert resp['limit'] == 10
        assert len(resp['results']) == min(expected_total, 10)
        assert resp['total'] == expected_total

    @pytest.mark.parametrize('field', ['created_at', 'modified_at'])
    @pytest.mark.parametrize('model',
                             [
                                 (model)
                                 for model in ENTITY_ENDPOINT_MAP.keys()
                             ])
    def test_generated_date_filters(self, client, entities, model, field):
        """
        Test retrieving entities w created_at and modified_at filters
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]
        entity = model.query.first()
        filter_params = {field: self._datetime_string(getattr(entity, field))}

        # Get expected total
        expected_total = 1

        # Make query string
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 200
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert resp['limit'] == 10
        assert len(resp['results']) == min(expected_total, 10)
        assert resp['total'] == expected_total
        # All results have correct field values
        for result in resp['results']:
            for k, v in filter_params.items():
                d = parser.parse(v).replace(tzinfo=tz.tzutc())
                assert parser.parse(result.get(k)) == (d)

    @pytest.mark.parametrize('invalid_params', [{'created_at': 'hello'},
                                                {'created_at': 92374},
                                                {'modified_at': 'hello'},
                                                {'modified_at': 92374},
                                                ])
    @pytest.mark.parametrize('model',
                             [
                                 (model)
                                 for model in ENTITY_ENDPOINT_MAP.keys()
                             ])
    def test_invalid_gen_date_filters(self, client, entities, model,
                                      invalid_params):
        """
        Test retrieving entities w created_at and modified_at filters
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]

        # Make query string
        qs = urlencode(invalid_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 400
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert ('could not retrieve entities:' in
                resp['_status']['message'])
        for k, v in invalid_params.items():
            assert k in resp['_status']['message']

    def _datetime_string(self, dt):
        return 'T'.join(str(dt).split(' ')).split('+')[0]
