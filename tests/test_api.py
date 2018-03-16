import json
import pkg_resources
import pytest

from dataservice.api.common import id_service


class TestAPI:
    """
    General API tests such as reponse code checks, envelope formatting checks,
    and header checks
    """

    @pytest.mark.parametrize('endpoint,method,status_code', [
        ('/status', 'GET', 200),
        ('/aliquots', 'GET', 200),
        ('/aliquots/123', 'GET', 404),
        ('/samples', 'GET', 200),
        ('/samples/123', 'GET', 404),
        ('/diagnoses', 'GET', 200),
        ('/diagnoses/123', 'GET', 404),
        ('/demographics', 'GET', 200),
        ('/demographics/123', 'GET', 404),
        ('/phenotypes', 'GET', 200),
        ('/phenotypes/123', 'GET', 404),
        ('/participants', 'GET', 200),
        ('/persons', 'GET', 404),
        ('/participants/123', 'GET', 404),
        ('/studies', 'GET', 200),
        ('/studies/123', 'GET', 404),
        ('/investigators', 'GET', 200),
        ('/outcomes', 'GET', 200),
        ('/outcomes/123', 'GET', 404)
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
        ('/aliquots', 'GET', 'success'),
        ('/aliquots/123', 'GET', 'could not find aliquot `123`'),
        ('/aliquots/123', 'PATCH', 'could not find aliquot `123`'),
        ('/aliquots/123', 'DELETE', 'could not find aliquot `123`'),
        ('/samples', 'GET', 'success'),
        ('/samples/123', 'GET', 'could not find sample `123`'),
        ('/samples/123', 'PATCH', 'could not find sample `123`'),
        ('/samples/123', 'DELETE', 'could not find sample `123`'),
        ('/diagnoses', 'GET', 'success'),
        ('/diagnoses/123', 'GET', 'could not find diagnosis `123`'),
        ('/diagnoses/123', 'PATCH', 'could not find diagnosis `123`'),
        ('/diagnoses/123', 'DELETE', 'could not find diagnosis `123`'),
        ('/demographics', 'GET', 'success'),
        ('/demographics/123', 'GET', 'could not find demographic `123`'),
        ('/demographics/123', 'PATCH', 'could not find demographic `123`'),
        ('/demographics/123', 'DELETE', 'could not find demographic `123`'),
        ('/phenotypes', 'GET', 'success'),
        ('/phenotypes/123', 'GET', 'could not find phenotype `123`'),
        ('/phenotypes/123', 'PATCH', 'could not find phenotype `123`'),
        ('/phenotypes/123', 'DELETE', 'could not find phenotype `123`'),
        ('/participants', 'GET', 'success'),
        ('/participants/123', 'GET', 'could not find participant `123`'),
        ('/participants/123', 'PATCH', 'could not find participant `123`'),
        ('/participants/123', 'DELETE', 'could not find participant `123`'),
        ('/studies', 'GET', 'success'),
        ('/studies/123', 'GET', 'could not find study `123`'),
        ('/studies/123', 'PATCH', 'could not find study `123`'),
        ('/studies/123', 'DELETE', 'could not find study `123`'),
        ('/investigators', 'GET', 'success'),
        ('/investigators/123', 'GET', 'could not find investigator `123`'),
        ('/investigators/123', 'PATCH', 'could not find investigator `123`'),
        ('/investigators/123', 'DELETE', 'could not find investigator `123`'),
        ('/outcomes', 'GET', 'success'),
        ('/outcomes/123', 'GET', 'could not find outcome `123`'),
        ('/outcomes/123', 'PATCH', 'could not find outcome `123`'),
        ('/outcomes/123', 'DELETE', 'could not find outcome `123`')
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
        ('/aliquots', 'GET'),
        ('/samples', 'GET'),
        ('/diagnoses', 'GET'),
        ('/demographics', 'GET'),
        ('/studies', 'GET'),
        ('/investigators', 'GET'),
        ('/participants', 'GET'),
        ('/outcomes', 'GET'),
        ('/studies', 'GET'),
        ('/phenotypes', 'GET')
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

    @pytest.mark.parametrize('endpoint, method, fields', [
        ('/participants', 'POST', ['created_at', 'modified_at']),
        ('/participants', 'PATCH', ['created_at', 'modified_at']),
        ('/demographics', 'PATCH', ['created_at', 'modified_at']),
        ('/diagnoses', 'PATCH', ['created_at', 'modified_at']),
        ('/samples', 'PATCH', ['created_at', 'modified_at']),
        ('/studies', 'POST', ['created_at', 'modified_at']),
        ('/studies', 'PATCH', ['created_at', 'modified_at']),
        ('/outcomes', 'POST', ['created_at', 'modified_at']),
        ('/outcomes', 'PATCH', ['created_at', 'modified_at']),
        ('/phenotypes', 'PATCH', ['created_at', 'modified_at']),
        ('/investigators', 'PATCH', ['created_at', 'modified_at']),
        ('/aliquots', 'PATCH', ['created_at', 'modified_at'])
    ])
    def test_read_only(self, client, entities, endpoint, method, fields):
        """ Test that given fields can not be written or modified """
        inputs = entities[endpoint]
        method_name = method.lower()
        [inputs.update({field: 'test'}) for field in fields]
        call_func = getattr(client, method_name)
        kwargs = {'data': json.dumps(inputs),
                  'headers': {'Content-Type': 'application/json'}}
        if method_name in {'put', 'patch'}:
            kf_id = entities.get('kf_ids').get(endpoint)
            endpoint = '{}/{}'.format(endpoint, kf_id)
        resp = call_func(endpoint, **kwargs)
        body = json.loads(resp.data.decode('utf-8'))
        for field in fields:
            assert (field not in body['results']
                    or body['results'][field] != 'test')

    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('endpoint', ['/participants',
                                          '/demographics',
                                          '/diagnoses',
                                          '/samples',
                                          '/studies',
                                          '/investigators',
                                          '/outcomes',
                                          '/phenotypes',
                                          '/aliquots'])

    def test_unknown_field(self, client, entities, endpoint, method):
        """ Test that unknown fields are rejected when trying to create  """
        inputs = entities[endpoint]
        inputs.update({'blah': 'test'})
        action = 'create'
        if method.lower() in {'put', 'patch'}:
            action = 'update'
            kf_id = entities.get('kf_ids').get(endpoint)
            endpoint = '{}/{}'.format(endpoint, kf_id)
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint, data=json.dumps(inputs),
                         headers={'Content-Type': 'application/json'})

        body = json.loads(resp.data.decode('utf-8'))
        assert body['_status']['code'] == 400
        assert 'could not {} '.format(action) in body['_status']['message']
        assert 'Unknown field' in body['_status']['message']

    @pytest.mark.parametrize('resource,field', [
        ('/participants', 'demographic'),
        ('/participants', 'diagnoses'),
        ('/participants', 'samples'),
        ('/samples', 'aliquots'),
        ('/participants', 'outcomes'),
    ])
    def test_relations(self, client, entities, resource, field):
        """ Checks that references to other resources have correct ID """
        kf_id = entities.get('kf_ids').get(resource)
        resp = client.get(resource + '/' + kf_id)
        body = json.loads(resp.data.decode('utf-8'))['results']

        assert field in body
        if type(body[field]) is list:
            assert all([type(f) is str for f in body[field]])
            assert all([len(f) == 11 for f in body[field]])
        else:
            assert type(body[field]) is str
            assert len(body[field]) == 11

    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('endpoint, field, value',
                             [('/aliquots', 'shipment_date', 12000),
                              ('/aliquots', 'shipment_date', '12000'),
                              ('/aliquots', 'shipment_date', 'hai der'),
                              ('/aliquots', 'concentration', -12),
                              ('/aliquots', 'volume', -12),
                              ('/outcomes', 'age_at_event_days', -12)])
    def test_bad_input(self, client, entities, endpoint, method, field, value):
        """ Tests bad inputs """
        inputs = entities[endpoint]
        inputs.update({field: value})
        action = 'create'
        if method.lower() in {'put', 'patch'}:
            action = 'update'
            kf_id = entities.get('kf_ids').get(endpoint)
            endpoint = '{}/{}'.format(endpoint, kf_id)
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint, data=json.dumps(inputs),
                         headers={'Content-Type': 'application/json'})

        body = json.loads(resp.data.decode('utf-8'))
        assert body['_status']['code'] == 400
        assert 'could not {} '.format(action) in body['_status']['message']

    @pytest.mark.parametrize('method', ['POST'])
    @pytest.mark.parametrize('endpoint, field',
                             [('/aliquots', 'sample_id'),
                              ('/aliquots', 'analyte_type')])
    def test_missing_required_params(self, client, entities, endpoint,
                                     method, field):
        """ Tests missing required parameters """
        inputs = entities[endpoint]
        inputs.pop(field, None)
        action = 'create'
        if method.lower() in {'put'}:
            action = 'update'
            kf_id = entities.get('kf_ids').get(endpoint)
            endpoint = '{}/{}'.format(endpoint, kf_id)
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint, data=json.dumps(inputs),
                         headers={'Content-Type': 'application/json'})

        body = json.loads(resp.data.decode('utf-8'))
        assert body['_status']['code'] == 400
        assert 'could not {} '.format(action) in body['_status']['message']

    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('endpoint, field',
                             [('/aliquots', 'sample_id'),
                             ('/outcomes', 'participant_id')])
    def test_bad_foreign_key(self, client, entities, endpoint, method, field):
        """
        Test bad foreign key
        Foregin key is a valid kf_id but refers an entity that doesn't exist
        """
        inputs = entities[endpoint]
        inputs.update({field: id_service.kf_id_generator('ZZ')()})
        if method.lower() in {'put', 'patch'}:
            kf_id = entities.get('kf_ids').get(endpoint)
            endpoint = '{}/{}'.format(endpoint, kf_id)
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint, data=json.dumps(inputs),
                         headers={'Content-Type': 'application/json'})

        body = json.loads(resp.data.decode('utf-8'))
        assert body['_status']['code'] == 400
        assert 'does not exist' in body['_status']['message']

    def test_version(self, client):
        """ Test response from /status returns correct fields """
        status = json.loads(client.get('/status').data.decode('utf-8'))
        status = status['_status']
        assert 'commit' in status
        assert len(status['commit']) == 7
        assert 'branch' in status
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

        docs = json.loads(client.get('/swagger').data.decode('utf-8'))
        docs_version = docs['info']['version']

        assert docs_version == api_version
        assert docs_version == package

    def test_documentation(self, client):
        resp = client.get('')
        assert 'ReDoc' in resp.data.decode('utf-8')
        resp = client.get('/')
        assert 'ReDoc' in resp.data.decode('utf-8')
        resp = client.get('/docs')
        assert 'ReDoc' in resp.data.decode('utf-8')
