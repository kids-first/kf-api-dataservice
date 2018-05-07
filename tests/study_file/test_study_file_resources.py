import pytest
import json
import uuid
from unittest.mock import MagicMock
from requests.exceptions import HTTPError

from flask import url_for

from dataservice.extensions import db
from dataservice.api.study_file.models import StudyFile
from dataservice.api.study.models import Study
from tests.utils import FlaskTestCase

STUDY_FILE_URL = 'api.study_files'
STUDY_FILE_LIST_URL = 'api.study_files_list'


@pytest.fixture
def study_files(client, entities):

    props = {
        'file_name': 'my_data.csv',
        'study_id': Study.query.first().kf_id,
        'size': 1024,
        'availability': 'Immediate Download',
        'urls': ['s3://mystudy/my_data.csv'],
        'hashes': {
            'md5': str(uuid.uuid4()).replace('-', '')
        }
    }
    for _ in range(102):
        resp = client.post(url_for(STUDY_FILE_LIST_URL),
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(props))
        assert resp.status_code == 201

    assert StudyFile.query.count() == 103


@pytest.mark.usefixtures("indexd")
def _new_study_file(client):
    """ Creates a study file """
    body = {
        'file_name': 'my_data.csv',
        'study_id': Study.query.first().kf_id,
        'data_type': 'clinical',
        'file_format': 'csv',
        'availability': 'Immediate Download',
        'size': 1024,
        'urls': ['s3://mystudy/my_data.csv'],
        'hashes': {
            'md5': str(uuid.uuid4()).replace('-', '')
        }
    }
    response = client.post(url_for(STUDY_FILE_LIST_URL),
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(body))
    resp = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 201
    return resp


def test_new(client, indexd, entities):
    """
    Test creating a new study file
    """
    orig_calls = indexd.post.call_count
    resp = _new_study_file(client)
    assert 'study_file' in resp['_status']['message']
    assert 'created' in resp['_status']['message']
    assert resp['results']['file_name'] == 'my_data.csv'

    study_file = resp['results']
    sf = StudyFile.query.get(study_file['kf_id'])
    assert sf
    assert indexd.post.call_count == orig_calls + 1


def test_get_list(client, study_files, indexd):
    """
    Test that study files are returned in a paginated list with all
    info loaded from indexd
    """

    resp = client.get(url_for(STUDY_FILE_LIST_URL))
    resp = json.loads(resp.data.decode('utf-8'))

    assert resp['_status']['code'] == 200
    assert resp['total'] == StudyFile.query.count()
    assert len(resp['results']) == 10
    assert indexd.get.call_count == 10


def test_get_list_with_missing_files(client, indexd, study_files):
    """
    Test that study files that are not found in indexd are automatically
    deleted
    """
    response_mock = MagicMock()
    response_mock.status_code = 404
    response_mock.json.return_value = {'error': 'no record found'}

    def get(*args, **kwargs):
        return response_mock
    indexd.get.side_effect = get

    resp = client.get(url_for(STUDY_FILE_LIST_URL))
    resp = json.loads(resp.data.decode('utf-8'))

    assert resp['_status']['code'] == 200
    assert resp['total'] == StudyFile.query.count()
    assert StudyFile.query.count() == 0
    # It's expected that all study files are removed and none are returned
    # since indexd says everything is deleted
    assert len(resp['results']) == 0
    for res in resp['results']:
        assert 'kf_id' in res
    assert indexd.get.call_count == 103


def test_get_one(client, entities):
    """
    Test that study files are returned in a paginated list with all
    info loaded from indexd
    """

    st = StudyFile.query.first()
    st.merge_indexd()

    resp = client.get(url_for(STUDY_FILE_URL, kf_id=st.kf_id))
    resp = json.loads(resp.data.decode('utf-8'))

    assert resp['_status']['code'] == 200
    resp = resp['results']
    # check properties from indexd
    assert resp['hashes'] == st.hashes
    assert resp['metadata'] == st._metadata
    assert 'rev' not in resp
    assert resp['size'] == st.size
    # check properties from datamodel
    assert resp['file_name'] == st.file_name
    assert resp['data_type'] == st.data_type
    assert resp['file_format'] == st.file_format


def test_update(client, indexd, entities):
    """
    Test updating an existing study file

    This will should create a new version in indexd
    """

    resp = _new_study_file(client)
    orig_calls = indexd.post.call_count
    participant = resp['results']
    kf_id = participant.get('kf_id')
    orig = resp['results']
    orig_st = StudyFile.query.get(kf_id)
    orig_uuid = orig_st.uuid
    orig_did = orig_st.latest_did

    body = {
        'file_name': 'hg37.bam',
        'size': 23498
    }

    response = client.patch(url_for(STUDY_FILE_URL,
                                    kf_id=kf_id),
                            data=json.dumps(body),
                            headers={'Content-Type': 'application/json'})

    assert indexd.post.call_count == orig_calls + 1
    assert indexd.post.called_with(orig_st.latest_did)

    assert response.status_code == 200

    resp = json.loads(response.data.decode("utf-8"))
    assert 'study_file' in resp['_status']['message']
    assert 'updated' in resp['_status']['message']

    # Test response
    st = resp['results']
    assert st['kf_id'] == kf_id
    assert st['file_name'] == body['file_name']

    # Test database object
    st = StudyFile.query.get(kf_id)
    st.merge_indexd()
    assert st.file_name, body['file_name']
    assert st.uuid == orig_uuid
    assert st.latest_did != orig_did


def test_delete(client, indexd, entities):
    """
    Test deleting a study_file by id
    """
    init = StudyFile.query.count()

    r = _new_study_file(client)
    kf_id = r['results']['kf_id']

    response = client.delete(url_for(STUDY_FILE_URL,
                                     kf_id=kf_id),
                             headers={'Content-Type': 'application/json'})

    resp = json.loads(response.data.decode("utf-8"))

    assert 'study_file' in resp['_status']['message']
    assert 'deleted' in resp['_status']['message']
    assert StudyFile.query.count() == init
    assert indexd.delete.call_count == 1


def test_delete_error(client, indexd, entities):
    """
    Test handling of indexd error
    """

    response_mock = MagicMock()
    response_mock.status_code = 500
    response_mock.json.return_value = {'error': 'fake error message'}

    def exc():
        raise HTTPError()
    response_mock.raise_for_status = exc
    indexd.delete.return_value = response_mock

    init = StudyFile.query.count()

    r = _new_study_file(client)
    kf_id = r['results']['kf_id']

    response = client.delete(url_for(STUDY_FILE_URL,
                                     kf_id=kf_id),
                             headers={'Content-Type': 'application/json'})

    resp = json.loads(response.data.decode("utf-8"))

    assert indexd.delete.call_count == 1
    assert 'fake error message' in resp['_status']['message']
    assert StudyFile.query.count() == init + 1
