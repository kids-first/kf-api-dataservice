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
        ('/status', 'GET', 200),
        ('/samples', 'GET', 200),
        ('/samples/123', 'GET', 404),
        ('/diagnoses', 'GET', 200),
        ('/diagnoses/123', 'GET', 404),
        ('/participants', 'GET', 200),
        ('/persons', 'GET', 404),
        ('/participants/123', 'GET', 404)
    ])
    def test_status_codes(self, client, endpoint, method, status_code):
        """ Test endpoint response codes """
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint)
        assert resp.status_code == status_code
        resp = resp.data.decode('utf-8')
        assert json.loads(resp)['_status']['code'] == status_code

    @pytest.mark.parametrize('endpoint,method,status_message', [
        ('/status', 'GET', 'Welcome to'),
        ('/persons', 'GET', 'not found'),
        ('/samples', 'GET', 'success'),
        ('/samples/123', 'GET', 'could not find sample `123`'),
        ('/samples/123', 'PUT', 'could not find sample `123`'),
        ('/samples/123', 'DELETE', 'could not find sample `123`'),
        ('/diagnoses', 'GET', 'success'),
        ('/diagnoses/123', 'GET', 'could not find diagnosis `123`'),
        ('/diagnoses/123', 'PUT', 'could not find diagnosis `123`'),
        ('/diagnoses/123', 'DELETE', 'could not find diagnosis `123`'),
        ('/participants', 'GET', 'success'),
        ('/participants/123', 'GET', 'could not find Participant `123`'),
        ('/participants/123', 'PUT', 'could not find Participant `123`'),
        ('/participants/123', 'DELETE', 'could not find Participant `123`')
    ])
    def test_status_messages(self, client, endpoint, method, status_message):
        """
        Test endpoint response messages by checking if the message
        returned from the server contains a given string
        """
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint)
        resp = json.loads(resp.data.decode('utf-8'))
        assert status_message in resp['_status']['message']

    @pytest.mark.parametrize('endpoint,method', [
        ('/participants', 'GET'),
        ('/samples', 'GET'),
        ('/diagnoses', 'GET')
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

    @pytest.mark.parametrize('endpoint,field', [
        ('/participants', 'created_at'),
        ('/participants', 'modified_at')
    ])
    def test_read_only(self, client, endpoint, field):
        """ Test that given fields can not be written or modified """
        req = {field: 'test'}
        resp = client.post(endpoint,
                data=json.dumps(req),
                headers={'Content-Type': 'application/json'})
        body = json.loads(resp.data.decode('utf-8'))
        assert (field not in body['results']
                or body['results'][field] != 'test')

    @pytest.mark.parametrize('endpoint,field', [
        ('/participants', 'blah'),
        ('/samples', 'blah')
    ])
    def test_unknown_field(self, client, endpoint, field):
        """ Test that unknown fields are rejected when trying to create  """
        req = {field: 'test'}
        resp = client.post(endpoint,
                data=json.dumps(req),
                headers={'Content-Type': 'application/json'})
        body = json.loads(resp.data.decode('utf-8'))
        assert body['_status']['code'] == 400
        assert 'could not create ' in body['_status']['message']
        assert 'Unknown field' in body['_status']['message']

    
    @pytest.mark.parametrize('resource,field', [
        ('/participants', 'demographic'),
        ('/participants', 'diagnoses')
    ])
    def test_relations(self, client, entities, resource, field):
        """ Checks that references to other resources have correct ID """
        resp = client.get(resource)
        body = json.loads(resp.data.decode('utf-8'))['results'][0]

        assert field in body
        if type(body[field]) is list:
            assert all([type(f) is str for f in body[field]])
            assert all([len(f) == 8 for f in body[field]])
        else:
            assert type(body[field]) is str
            assert len(body[field]) == 8

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
        api_version = json.loads(client.get('/status').data.decode('utf-8'))
        api_version = api_version['_status']['version']

        assert api_version == package

    def test_documentation(self, client):
        resp = client.get('')
        assert 'ReDoc' in resp.data.decode('utf-8')
        resp = client.get('/')
        assert 'ReDoc' in resp.data.decode('utf-8')
        resp = client.get('/docs')
        assert 'ReDoc' in resp.data.decode('utf-8')
