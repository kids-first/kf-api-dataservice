import json
import requests
from unittest.mock import patch
import pytest
from unittest.mock import MagicMock
from requests.exceptions import HTTPError

from flask import url_for

from dataservice.extensions import db
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_experiment.models import SequencingExperiment

from tests.mocks import MockIndexd


GENOMICFILE_URL = 'api.genomic_files'
GENOMICFILE_LIST_URL = 'api.genomic_files_list'


@pytest.fixture
def genomic_files(client, mocker, entities):
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    indexd = MockIndexd()
    mock.get = indexd.get
    mock.post = indexd.post

    props = {
        'file_name': 'hg38.bam',
        'data_type': 'aligned reads',
        'sequencing_experiment_id': SequencingExperiment.query.first().kf_id,
        'file_format': 'bam'
    }
    gfs = [GenomicFile(**props) for _ in range(102)]
    db.session.add_all(gfs)
    db.session.commit()


def test_new(client, mocker, entities):
    """
    Test creating a new genomic file
    """
    # Mock data returned from gen3
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    mock.post = MockIndexd().post

    resp = _new_genomic_file(client)
    assert 'genomic_file' in resp['_status']['message']
    assert 'created' in resp['_status']['message']
    assert resp['results']['file_name'] == 'hg38.bam'

    genomic_file = resp['results']
    assert GenomicFile.query.get(genomic_file['kf_id'])


def test_new_indexd_error(client, mocker, entities):
    """
    Test case when indexd errors
    """
    # Mock data returned from gen3
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    mock.post = MockIndexd(status_code=500).post

    body = {
        'file_name': 'hg38.bam',
        'size': 123,
        'data_type': 'aligned reads',
        'file_format': 'bam',
        'file_url': 's3://bucket/key',
        'md5sum': 'd418219b883fce3a085b1b7f38b01e37',
        'sequencing_experiment_id': 'SE_AAAAAAAA',
        'controlled_access': False
    }
    init_count = GenomicFile.query.count()
    response = client.post(url_for(GENOMICFILE_LIST_URL),
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(body))
    resp = json.loads(response.data.decode("utf-8"))

    assert 'could not register' in resp['_status']['message']
    assert GenomicFile.query.count() == init_count


def test_get_list(client, genomic_files, mocker):
    """
    Test that genomic files are returned in a paginated list with all
    info loaded from indexd
    """
    # Mock data returned from gen3
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    indexd = MockIndexd()
    mock.get = indexd.get
    mock.post = indexd.post

    resp = client.get(url_for(GENOMICFILE_LIST_URL))
    resp = json.loads(resp.data.decode('utf-8'))

    assert resp['_status']['code'] == 200
    assert resp['total'] == GenomicFile.query.count()
    assert len(resp['results']) == 10


def test_get_one(client, mocker, entities):
    """
    Test that genomic files are returned in a paginated list with all
    info loaded from indexd
    """
    # Mock data returned from gen3
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    indexd = MockIndexd()
    mock.get = indexd.get
    
    gf = GenomicFile.query.first()
    gf.merge_indexd()

    resp = client.get(url_for(GENOMICFILE_URL, kf_id=gf.kf_id))
    resp = json.loads(resp.data.decode('utf-8'))

    assert resp['_status']['code'] == 200
    resp = resp['results']
    # check properties from indexd
    assert resp['hashes'] == gf.hashes
    assert resp['metadata'] == gf._metadata
    assert resp['rev'] == gf.rev
    assert resp['size'] == gf.size
    # check properties from datamodel
    assert resp['file_name'] == gf.file_name
    assert resp['data_type'] == gf.data_type
    assert resp['file_format'] == gf.file_format


def test_update(client, mocker, entities):
    """
    Test updating an existing genomic file
    """
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    indexd = MockIndexd()
    mock.post = indexd.post
    mock.get = indexd.get
    mock.patch = indexd.patch

    resp = _new_genomic_file(client)
    participant = resp['results']
    kf_id = participant.get('kf_id')
    orig = resp['results']

    body = {
        'file_name': 'hg37.bam'
    }
    response = client.patch(url_for(GENOMICFILE_URL,
                                  kf_id=kf_id),
                               data=json.dumps(body),
                          headers={'Content-Type': 'application/json'})

    assert response.status_code == 200

    resp = json.loads(response.data.decode("utf-8"))
    assert 'genomic_file' in resp['_status']['message']
    assert 'updated' in resp['_status']['message']

    gf = resp['results']
    assert gf['kf_id'] == kf_id
    assert gf['file_name'] == body['file_name']

    gf = GenomicFile.query.first()
    assert gf.file_name, body['file_name']


def test_delete(client, mocker, entities):
    """
    Test deleting a participant by id
    """
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    indexd = MockIndexd()
    mock.get = indexd.get
    mock.post = indexd.post

    init = GenomicFile.query.count()

    r = _new_genomic_file(client)
    kf_id = r['results']['kf_id']

    response = client.delete(url_for(GENOMICFILE_URL,
                                     kf_id=kf_id),
                             headers={'Content-Type': 'application/json'})

    resp = json.loads(response.data.decode("utf-8"))

    assert mock.delete.call_count == 1
    assert 'genomic_file' in resp['_status']['message']
    assert 'deleted' in resp['_status']['message']
    assert GenomicFile.query.count() == init


def test_delete_error(client, mocker, entities):
    """
    Test handling of indexd error
    """
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    indexd = MockIndexd()
    mock.get = indexd.get
    mock.post = indexd.post

    response_mock = MagicMock()
    response_mock.status_code = 500
    def exc():
        raise HTTPError()
    response_mock.raise_for_status = exc
    mock.delete.return_value = response_mock

    init = GenomicFile.query.count()

    r = _new_genomic_file(client)
    kf_id = r['results']['kf_id']

    response = client.delete(url_for(GENOMICFILE_URL,
                                     kf_id=kf_id),
                             headers={'Content-Type': 'application/json'})

    resp = json.loads(response.data.decode("utf-8"))

    assert mock.delete.call_count == 1
    assert 'could not delete genomic_file' in resp['_status']['message']
    assert GenomicFile.query.count() == init + 1


def _new_genomic_file(client):
    """ Creates a genomic file """
    body = {
        'file_name': 'hg38.bam',
        'size': 123,
        'data_type': 'aligned reads',
        'file_format': 'bam',
        'file_url': 's3://bucket/key',
        'md5sum': 'd418219b883fce3a085b1b7f38b01e37',
        'sequencing_experiment_id': SequencingExperiment.query.first().kf_id,
        'controlled_access': False
    }
    response = client.post(url_for(GENOMICFILE_LIST_URL),
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(body))
    resp = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 201
    return resp
