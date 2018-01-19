import json
import pkg_resources
import pytest

import dataservice


class TestAPI:
    """
    General API tests such as reponse code checks, envelope formatting checks,
    and header checks
    """

    @pytest.mark.parametrize('endpoint,method,status_code', [
        ('/', 'GET', 200),
        ('', 'GET', 200),
        ('/status', 'GET', 200),
        ('/persons', 'GET', 200),
        ('/persons/123', 'GET', 404)
    ])
    def test_status_codes(self, client, endpoint, method, status_code):
        """ Test endpoint response codes """
        call_func = getattr(client, method.lower())
        assert call_func(endpoint).status_code == status_code


    @pytest.mark.parametrize('endpoint,method', [
        ('/persons', 'GET')
    ])
    def test_status_format(self, client, endpoint, method):
        """ Test that the _response field is consistent """
        call_func = getattr(client, method.lower())
        body = json.loads(call_func(endpoint).data.decode('utf-8'))
        assert '_status' in body
        assert 'message' in body['_status']
        assert type(body['_status']['message']) is str
        assert 'code' in body['_status']
        assert type(body['_status']['code']) is int

    def test_version(self, client):
        """ Test response from /status returns correct fields """
        status = json.loads(client.get('/status').data.decode('utf-8'))
        status = status['_status']
        assert 'commit' in status
        assert len(status['commit']) == 7
        assert 'version' in status
        assert status['version'].count('.') == 2
        assert 'tags' in status
        assert type(status['tags']) is list
        assert 'Dataservice' in status['message']

    def test_versions(self, client):
        """ Test that versions are aligned accross package, docs, and api """
        package = pkg_resources.get_distribution("kf-api-dataservice").version
        api_restplus = dataservice.api.api.version
        api_version = json.loads(client.get('/status').data.decode('utf-8'))
        api_version = api_version['_status']['version']
        swagger = json.loads(client.get('/swagger.json').data.decode('utf-8'))

        assert api_version == package
        assert api_version == api_restplus 
        assert api_version == swagger['info']['version']
