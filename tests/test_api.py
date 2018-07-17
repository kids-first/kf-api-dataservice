import json
import pkg_resources
import pytest

from dataservice.api.common import id_service
from tests.conftest import (
    ENDPOINT_ENTITY_MAP,
    ENDPOINTS,
    ENTITY_PARAMS,
    _add_foreign_keys
)


class TestAPI:
    """
    General API tests such as reponse code checks, envelope formatting checks,
    and header checks
    """
    @pytest.mark.parametrize('endpoint', ENDPOINTS)
    def test_no_content_type(self, client, endpoint):
        """ Test that no 500 is thrown when the content isnt specified """
        resp = client.post(endpoint, data='{}')
        assert resp.status_code < 500
        resp = client.patch(endpoint, data='{}')
        assert resp.status_code < 500

    @pytest.mark.parametrize('endpoint,method,status_code',
                             [(ept, 'GET', 200) for ept in ENDPOINTS] +
                             [(ept + '/123', 'GET', 404) for ept in ENDPOINTS]
                             )
    def test_status_codes(self, client, endpoint, method, status_code):
        """ Test endpoint response codes """
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint)
        assert resp.status_code == status_code
        resp = resp.data.decode('utf-8')
        assert json.loads(resp)['_status']['code'] == status_code

    @pytest.mark.parametrize('endpoint,method,status_message',
                             [('/status', 'GET', 'Welcome to'),
                              ('/persons', 'GET',
                               'The requested URL was not found')] +
                             [(ept, 'GET', 'success')
                              for ept in ENDPOINTS] +
                             [(ept + '/123', 'GET', 'could not find')
                              for ept in ENDPOINTS] +
                             [(ept + '/123', 'PATCH', 'could not find')
                              for ept in ENDPOINTS] +
                             [(ept + '/123', 'DELETE', 'could not find')

                              for ept in ENDPOINTS]
                             )
    def test_status_messages(self, client, endpoint, method, status_message):
        """
        Test endpoint response messages by checking if the message
        returned from the server contains a given string
        """
        call_func = getattr(client, method.lower())
        resp = call_func(endpoint, data='{}')
        resp = json.loads(resp.data.decode('utf-8'))
        assert resp['_status']['message'].startswith(status_message)

    @pytest.mark.parametrize('endpoint,method',
                             [(ept, 'GET') for ept in ENDPOINTS]
                             )
    def test_status_format(self, client, endpoint, method):
        """ Test that the _response field is consistent """
        call_func = getattr(client, method.lower())
        body = json.loads(call_func(endpoint).data.decode('utf-8'))
        assert '_status' in body
        assert 'message' in body['_status']
        assert type(body['_status']['message']) is str
        assert 'code' in body['_status']
        assert type(body['_status']['code']) is int

    @pytest.mark.parametrize('endpoint, parents', [
        ('/studies', ['investigator']),
        ('/study-files', ['study']),
        ('/investigators', []),
        ('/participants', ['study', 'family']),
        ('/family-relationships', ['participant1', 'participant2']),
        ('/phenotypes', ['participant']),
        ('/outcomes', ['participant']),
        ('/diagnoses', ['participant', 'biospecimen']),
        ('/biospecimens', ['participant', 'sequencing_center']),
        ('/sequencing-experiments', ['sequencing_center']),
        ('/genomic-files', ['biospecimen',
                            'sequencing_experiment',
                            'read_group']),
        ('/read-groups', ['genomic_file']),
        ('/cavatica-tasks', ['cavatica_app']),
        ('/cavatica-task-genomic-files', ['cavatica_task', 'genomic_file']),
        ('/biospecimen-genomic-files', ['biospecimen', 'genomic_file'])
    ])
    def test_parent_links(self, client, entities, endpoint, parents):
        """ Test the existance and formatting of _links """
        # Setup inputs
        model_cls = ENDPOINT_ENTITY_MAP.get(endpoint)
        entity = entities.get(model_cls)[0]
        resp = client.get(endpoint + '/' + entity.kf_id,
                          headers={'Content-Type': 'application/json'})

        body = json.loads(resp.data.decode('utf-8'))
        # All links are formatted properly
        assert '_links' in body
        for parent in parents:
            # Links formatted properly
            assert parent in body['_links']
            link = body['_links'][parent]
            if link:
                assert len(link.split('/')[-1]) == 11

        # Test self and collection links
        assert 'collection' in body['_links']
        assert body['_links']['collection'] == endpoint
        assert 'self' in body['_links']
        self_link = body['_links']['self']
        self_kf_id = self_link.split('/')[-1]
        self_endpoint = '/' + self_link.split('/')[1]
        self_model_cls = ENDPOINT_ENTITY_MAP.get(self_endpoint)
        assert self_model_cls.query.get(self_kf_id)

    @pytest.mark.parametrize('endpoint,child_relations', [
        ('/studies', ['study_files', 'participants']),
        ('/investigators', ['studies']),
        ('/families', ['participants']),
        ('/sequencing-centers', ['sequencing_experiments', 'biospecimens']),
        ('/participants', ['diagnoses', 'phenotypes', 'outcomes',
                           'biospecimens']),
        ('/biospecimens', ['genomic_files', 'diagnoses']),
        ('/sequencing-experiments', ['genomic_files']),
        ('/genomic-files', ['cavatica_task_genomic_files',
                            'biospecimen_genomic_files']),
        ('/cavatica-apps', ['cavatica_tasks']),
        ('/cavatica-tasks', ['cavatica_task_genomic_files']),
    ])
    def test_child_links(self, client, entities, endpoint, child_relations):
        """ Checks that references to other resources have correct ID """
        # Setup inputs
        model_cls = ENDPOINT_ENTITY_MAP.get(endpoint)
        entity = entities.get(model_cls)[0]

        resp = client.get(endpoint + '/' + entity.kf_id)
        links = json.loads(resp.data.decode('utf-8'))['_links']
        for child in child_relations:
            # Child entity exists in links
            assert child in links
            # Format of link
            link = links[child]
            link_endpoint = link.split('?')[0]
            assert ('/' + child.replace('_', '-')) == link_endpoint
            assert type(link) is str
            kf_id = link.split('=')[-1]
            assert len(kf_id) == 11
            # Foreign key exists
            foreign_key = link.split('?')[-1].split('=')[0]
            related_entity_cls = ENDPOINT_ENTITY_MAP[link_endpoint]
            assert getattr(related_entity_cls, foreign_key)

    @pytest.mark.parametrize('endpoint', ENDPOINTS)
    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('fields', [['created_at', 'modified_at']])
    def test_read_only(self, client, entities, endpoint, method, fields):
        """ Test that given fields can not be written or modified """
        # Setup inputs
        inputs = ENTITY_PARAMS['fields'][endpoint].copy()
        model_cls = ENDPOINT_ENTITY_MAP.get(endpoint)
        entity = entities.get(model_cls)[0]
        _add_foreign_keys(inputs, entity)
        [inputs.update({field: 'test'}) for field in fields]

        # Setup enpdoint
        url = endpoint
        method_name = method.lower()
        call_func = getattr(client, method_name)
        kwargs = {'data': json.dumps(inputs),
                  'headers': {'Content-Type': 'application/json'}}
        if method_name in {'put', 'patch'}:
            kf_id = entity.kf_id
            url = '{}/{}'.format(endpoint, kf_id)

        # Send request
        resp = call_func(url, **kwargs)
        body = json.loads(resp.data.decode('utf-8'))

        if 'results' not in body:
            assert ('error saving' in body['_status']['message'] or
                    'already exists' in body['_status']['message'])
            return
        for field in fields:
            assert (field not in body['results']
                    or body['results'][field] != 'test')

    @pytest.mark.parametrize('endpoint', ENDPOINTS)
    def test_predefined_kf_id(self, client, endpoint):
        """ Check that posting predefined kf_id doesn't 500 """
        resp = client.post(endpoint,
                           data=json.dumps({'kf_id': 'XX_00000000'}),
                           headers={'Content-Type': 'application/json'})
        assert resp.status_code != 500

    @pytest.mark.parametrize('endpoint', ENDPOINTS)
    @pytest.mark.parametrize('kf_id', ['XX_00000000', 'SD_ILOU0000', 'SD_01'])
    def test_malformed_predefined_kf_id(self, client, endpoint, kf_id):
        """ Check that posting malformed predefined kf_id doesn't 500 """
        resp = client.post(endpoint,
                           data=json.dumps({'kf_id': kf_id,
                                            'external_id': 'blah'}),
                           headers={'Content-Type': 'application/json'})
        assert resp.status_code == 400
        resp = json.loads(resp.data.decode('utf-8'))
        assert 'Invalid kf_id' in resp['_status']['message']

    @pytest.mark.parametrize('field', ['uuid'])
    @pytest.mark.parametrize('endpoint', ENDPOINTS)
    def test_excluded_field(self, client, entities, field, endpoint):
        """ Test that certain fields are excluded from serialization """
        body = json.loads(client.get(endpoint).data.decode('utf-8'))
        for res in body['results']:
            assert field not in res

    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('endpoint', ENDPOINTS)
    def test_unknown_field(self, client, entities, endpoint, method):
        """ Test that unknown fields are rejected when trying to create  """
        # Setup inputs
        inputs = ENTITY_PARAMS['fields'][endpoint].copy()
        model_cls = ENDPOINT_ENTITY_MAP.get(endpoint)
        entity = entities.get(model_cls)[0]
        _add_foreign_keys(inputs, entity)
        inputs.update({'blah': 'test'})

        # Setup endpoint
        url = endpoint
        action = 'create'
        if method.lower() in {'put', 'patch'}:
            action = 'update'
            kf_id = entity.kf_id
            url = '{}/{}'.format(endpoint, kf_id)
        call_func = getattr(client, method.lower())
        resp = call_func(url, data=json.dumps(inputs),
                         headers={'Content-Type': 'application/json'})

        body = json.loads(resp.data.decode('utf-8'))
        assert body['_status']['code'] == 400
        assert 'could not {} '.format(action) in body['_status']['message']
        assert 'Unknown field' in body['_status']['message']

    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('endpoint, invalid_params',
                             [(endpoint, invalid_param)
                              for endpoint in ENDPOINTS
                                 for invalid_param in ENTITY_PARAMS.get(
                                 'filter_params')[endpoint]['invalid']
                              ])
    def test_bad_input(self, client, entities, endpoint, invalid_params,
                       method):
        """ Tests bad inputs """
        # Setup inputs
        inputs = ENTITY_PARAMS['fields'][endpoint].copy()
        model_cls = ENDPOINT_ENTITY_MAP.get(endpoint)
        entity = entities.get(model_cls)[0]
        _add_foreign_keys(inputs, entity)
        inputs.update(invalid_params)

        # Setup endpoint
        url = endpoint
        action = 'create'
        if method.lower() in {'put', 'patch'}:
            action = 'update'
            kf_id = entity.kf_id
            url = '{}/{}'.format(endpoint, kf_id)
        call_func = getattr(client, method.lower())

        # Send request
        resp = call_func(url, data=json.dumps(inputs),
                         headers={'Content-Type': 'application/json'})

        body = json.loads(resp.data.decode('utf-8'))
        assert body['_status']['code'] == 400
        assert 'could not {} '.format(action) in body['_status']['message']

    @pytest.mark.parametrize('method', ['POST'])
    @pytest.mark.parametrize('endpoint, field',
                             [
                                 ('/family-relationships', 'participant1_id'),
                                 ('/family-relationships', 'participant2_id'),
                                 ('/study-files', 'study_id'),
                                 ('/study-files', 'urls'),
                                 ('/study-files', 'hashes'),
                                 ('/study-files', 'size'),
                                 ('/genomic-files', 'urls'),
                                 ('/genomic-files', 'hashes'),
                                 ('/read-groups', 'genomic_file_id'),
                                 ('/diagnoses', 'participant_id'),
                                 ('/sequencing-centers', 'name')
                             ])
    def test_missing_required_params(self, client, entities, endpoint,
                                     method, field):
        """ Tests missing required parameters """
        # Setup inputs
        inputs = ENTITY_PARAMS['fields'][endpoint].copy()
        model_cls = ENDPOINT_ENTITY_MAP.get(endpoint)
        entity = entities.get(model_cls)[0]
        _add_foreign_keys(inputs, entity)
        inputs.pop(field, None)

        # Setup endpoint
        url = endpoint
        action = 'create'
        if method.lower() in {'put'}:
            action = 'update'
            kf_id = entities.get('kf_ids').get(endpoint)
            url = '{}/{}'.format(endpoint, kf_id)
        call_func = getattr(client, method.lower())
        resp = call_func(url, data=json.dumps(inputs),
                         headers={'Content-Type': 'application/json'})

        body = json.loads(resp.data.decode('utf-8'))
        assert body['_status']['code'] == 400
        assert 'could not {} '.format(action) in body['_status']['message']

    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('endpoint, field',
                             [('/outcomes', 'participant_id'),
                              ('/phenotypes', 'participant_id'),
                              ('/family-relationships', 'participant1_id'),
                              ('/family-relationships', 'participant2_id'),
                              ('/study-files', 'study_id'),
                              ('/diagnoses', 'participant_id'),
                              ('/diagnoses', 'biospecimen_id'),
                              ('/biospecimens', 'participant_id'),
                              ('/genomic-files', 'biospecimen_id'),
                              ('/genomic-files', 'sequencing_experiment_id'),
                              ('/read-groups', 'genomic_file_id'),
                              ('/cavatica-tasks', 'cavatica_app_id'),
                              ('/cavatica-task-genomic-files',
                               'cavatica_task_id'),
                              ('/cavatica-task-genomic-files',
                               'genomic_file_id'),
                              ('/biospecimen-genomic-files',
                               'biospecimen_id'),
                              ('/biospecimen-genomic-files',
                               'genomic_file_id')
                              ])
    def test_bad_foreign_key(self, client, entities, endpoint, method, field):
        """
        Test bad foreign key
        Foregin key is a valid kf_id but refers an entity that doesn't exist
        """
        # Setup inputs
        inputs = ENTITY_PARAMS['fields'][endpoint].copy()
        model_cls = ENDPOINT_ENTITY_MAP.get(endpoint)
        entity = entities.get(model_cls)[0]
        _add_foreign_keys(inputs, entity)
        inputs.update({field: id_service.kf_id_generator('ZZ')()})

        # Setup endpoint
        url = endpoint
        if method.lower() in {'put', 'patch'}:
            url = '{}/{}'.format(endpoint, entity.kf_id)
        call_func = getattr(client, method.lower())
        resp = call_func(url, data=json.dumps(inputs),
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
