import json
import pkg_resources
import pytest

from dataservice.api.common import id_service
from tests.conftest import ENDPOINTS


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
        ('/phenotypes', ['participant']),
        ('/outcomes', ['participant']),
        ('/diagnoses', ['participant']),
        ('/biospecimens', ['participant', 'sequencing_center']),
        ('/sequencing-experiments', ['sequencing_center']),
        ('/genomic-files', ['biospecimen', 'sequencing_experiment']),
        ('/cavatica-tasks', ['cavatica_app']),
        ('/cavatica-task-genomic-files', ['cavatica_task', 'genomic_file'])
    ])
    def test_parent_links(self, client, entities, endpoint, parents):
        """ Test the existance and formatting of _links """
        resp = client.get(endpoint,
                          headers={'Content-Type': 'application/json'})
        body = json.loads(resp.data.decode('utf-8'))

        assert '_links' in body

        # If paginated results
        if isinstance(body['results'], list):
            for res in body['results']:
                assert '_links' in res
                # Parent entities are in links
                for p in parents:
                    assert p in res['_links']
                # All links are formatted properly
                for key, link in res['_links'].items():
                    if key == 'collection':
                        continue
                    if link:
                        assert len(link.split('/')[-1]) == 11
                    else:
                        assert link is None

    @pytest.mark.parametrize('endpoint', ENDPOINTS)
    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('fields', [['created_at', 'modified_at']])
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
        from pprint import pprint
        pprint(body)
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
                data=json.dumps({'kf_id': kf_id, 'external_id': 'blah'}),
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

    @pytest.mark.parametrize('resource,fields', [
        ('/sequencing-centers', ['sequencing_experiments', 'biospecimens']),
        ('/participants', ['diagnoses',
                           'phenotypes', 'outcomes', 'biospecimens']),
        ('/biospecimens', ['genomic_files']),
        ('/sequencing-experiments', ['genomic_files']),
        ('/studies', ['study_files', 'participants']),
        ('/investigators', ['studies']),
        ('/families', ['participants']),
        ('/cavatica-apps', ['cavatica_tasks']),
        ('/cavatica-tasks', ['cavatica_task_genomic_files']),
        ('/genomic-files', ['cavatica_task_genomic_files'])
    ])
    def test_child_links(self, client, entities, resource, fields):
        """ Checks that references to other resources have correct ID """
        kf_id = entities.get('kf_ids').get(resource)
        resp = client.get(resource + '/' + kf_id)
        body = json.loads(resp.data.decode('utf-8'))['results']
        for field in fields:
            assert field in body
            if type(body[field]) is list:
                assert all([type(f) is str for f in body[field]])
                assert all([len(f) == 11 for f in body[field]])
            else:
                assert type(body[field]) is str
                assert len(body[field]) == 11

    @pytest.mark.parametrize('method', ['POST', 'PATCH'])
    @pytest.mark.parametrize('endpoint, field, value',
                             [('/biospecimens', 'shipment_date', 12000),
                                 ('/biospecimens', 'shipment_date', '12000'),
                                 ('/biospecimens', 'shipment_date', 'hai der'),
                                 ('/biospecimens', 'concentration_mg_per_ml',
                                  -12),
                                 ('/biospecimens', 'volume_ml', -12),
                                 ('/outcomes', 'age_at_event_days', -12),
                                 ('/phenotypes', 'age_at_event_days', -12),
                                 ('/sequencing-experiments',
                                  'max_insert_size', -12),
                                 ('/sequencing-experiments',
                                  'mean_insert_size', -12),
                                 ('/sequencing-experiments',
                                  'mean_depth', -12),
                                 ('/sequencing-experiments',
                                  'mean_read_length', -12),
                                 ('/sequencing-experiments',
                                  'total_reads', -12),
                                 ('/sequencing-experiments',
                                  'experiment_date', 'hai der'),
                                 ('/cavatica-apps', 'revision', -5),
                                 ('/cavatica-apps', 'revision', 'hai der'),
                                 ('/cavatica-apps', 'github_commit_url',
                                  "github"),
                                 ('/cavatica-apps', 'github_commit_url',
                                     "www.google.com"),
                                 ('/cavatica-apps', 'github_commit_url',
                                     "http://"),
                                 ('/cavatica-task-genomic-files',
                                  'is_input', 'hai der'),
                                 ('/diagnoses', 'age_at_event_days', -5)
                              ])
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
                             [
                                 ('/biospecimens', 'analyte_type'),
                                 ('/family-relationships', 'participant_id'),
                                 ('/family-relationships', 'relative_id'),
                                 ('/study-files', 'study_id'),
                                 ('/study-files', 'urls'),
                                 ('/study-files', 'hashes'),
                                 ('/study-files', 'size'),
                                 ('/genomic-files', 'urls'),
                                 ('/genomic-files', 'hashes'),
                                 ('/genomic-files', 'size'),
                                 ('/diagnoses', 'participant_id'),
                                 ('/sequencing-centers', 'name')
                             ])
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
                             [('/outcomes', 'participant_id'),
                              ('/phenotypes', 'participant_id'),
                              ('/family-relationships', 'participant_id'),
                              ('/family-relationships', 'relative_id'),
                              ('/study-files', 'study_id'),
                              ('/diagnoses', 'participant_id'),
                              ('/biospecimens', 'participant_id'),
                              ('/genomic-files', 'biospecimen_id'),
                              ('/genomic-files', 'sequencing_experiment_id'),
                              ('/cavatica-tasks', 'cavatica_app_id'),
                              ('/cavatica-task-genomic-files',
                               'cavatica_task_id'),
                              ('/cavatica-task-genomic-files',
                               'genomic_file_id')
                              ])
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
        assert 'migration' in status
        assert len(status['migration']) == 12
        assert 'datamodel' in status
        assert status['datamodel'].count('.') == 2
        assert status['datamodel'].replace('.', '').isdigit()

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
