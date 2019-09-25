import json

import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError
from flask import url_for
from urllib.parse import urlencode

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.read_group.models import ReadGroup
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.genomic_file.models import GenomicFile
from tests.conftest import make_entities
from tests.conftest import ENTITY_TOTAL
from tests.mocks import MockIndexd


GENOMICFILE_URL = 'api.genomic_files'
GENOMICFILE_LIST_URL = 'api.genomic_files_list'
EXPECTED_TOTAL = ENTITY_TOTAL + 102 * 2


@pytest.fixture(scope='function')
def entities(client):
    return make_entities(client)


@pytest.yield_fixture(scope='function')
def client(app):
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    mock = patch('dataservice.extensions.flask_indexd.requests')
    mock = mock.start()
    indexd_mock = MockIndexd()
    mock.Session().get.side_effect = indexd_mock.get
    mock.Session().post.side_effect = indexd_mock.post

    mod = 'dataservice.api.study.models.requests'
    mock_bs = patch(mod)
    mock_bs = mock_bs.start()

    mock_resp_get = MagicMock()
    mock_resp_get.status_code = 200
    mock_resp_post = MagicMock()
    mock_resp_post.status_code = 201

    mock_bs.Session().get.side_effect = mock_resp_get
    mock_bs.Session().post.side_effect = mock_resp_post

    yield app.test_client()

    mock_bs.stop()
    mock.stop()
    # Need to make sure we close all connections so pg won't lock tables
    db.session.close()
    db.drop_all()


@pytest.fixture(scope='function')
def genomic_files(client, entities):

    props = {
        'external_id': 'genomic_file_0',
        'file_name': 'hg38.bam',
        'data_type': 'Aligned Reads',
        'file_format': 'bam'
    }
    gfs = [GenomicFile(**props) for _ in range(EXPECTED_TOTAL - ENTITY_TOTAL)]
    db.session.add_all(gfs)
    db.session.commit()
    db.session.expunge_all()


def test_new(client, indexd, entities):
    """
    Test creating a new genomic file
    """
    orig_calls = indexd.post.call_count
    resp = _new_genomic_file(client)
    assert 'genomic_file' in resp['_status']['message']
    assert 'created' in resp['_status']['message']
    assert resp['results']['file_name'] == 'hg38.bam'

    genomic_file = resp['results']
    gf = GenomicFile.query.get(genomic_file['kf_id'])
    assert gf
    assert indexd.post.call_count == orig_calls + 1


def test_new_indexd_error(client, entities):
    """
    Test case when indexd errors
    """

    body = {
        'external_id': 'genomic_file_0',
        'file_name': 'hg38.bam',
        'size': 123,
        'acl': ['TEST'],
        'authz': ['/projects/TEST'],
        'data_type': 'Aligned Reads',
        'file_format': 'bam',
        'urls': ['s3://bucket/key'],
        'controlled_access': False
    }
    init_count = GenomicFile.query.count()
    response = client.post(url_for(GENOMICFILE_LIST_URL),
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(body))

    resp = json.loads(response.data.decode("utf-8"))

    assert 400 == response.status_code
    assert 'could not create' in resp['_status']['message']
    assert GenomicFile.query.count() == init_count


def test_get_list(client, indexd, genomic_files):
    """
    Test that genomic files are returned in a paginated list with all
    info loaded from indexd
    """

    resp = client.get(url_for(GENOMICFILE_LIST_URL))
    resp = json.loads(resp.data.decode('utf-8'))

    assert resp['_status']['code'] == 200
    assert resp['total'] == GenomicFile.query.count()
    assert len(resp['results']) == 10
    assert indexd.get.call_count == 10


def test_get_list_with_missing_files(client, indexd, genomic_files):
    """
    Test that genomic files that are not found in indexd are automatically
    deleted
    """
    response_mock = MagicMock()
    response_mock.status_code = 404
    response_mock.json.return_value = {'error': 'no record found'}

    def get(*args, **kwargs):
        return response_mock
    indexd.get.side_effect = get

    resp = client.get(url_for(GENOMICFILE_LIST_URL))
    resp = json.loads(resp.data.decode('utf-8'))

    assert resp['_status']['code'] == 200
    assert resp['total'] == GenomicFile.query.count()
    assert GenomicFile.query.count() == 0
    # It's expected that all genomic files are removed and none are returned
    # since indexd says everything is deleted
    assert len(resp['results']) == 0
    for res in resp['results']:
        assert 'kf_id' in res
    expected = EXPECTED_TOTAL
    assert indexd.get.call_count == expected


def test_get_one(client, entities):
    """
    Test that genomic files are returned in a paginated list with all
    info loaded from indexd
    """

    gf = GenomicFile.query.first()
    gf.merge_indexd()

    resp = client.get(url_for(GENOMICFILE_URL, kf_id=gf.kf_id))
    resp = json.loads(resp.data.decode('utf-8'))

    assert resp['_status']['code'] == 200
    resp = resp['results']
    # check properties from indexd
    assert resp['hashes'] == gf.hashes
    assert resp['metadata'] == gf._metadata
    assert 'rev' not in resp
    assert resp['size'] == gf.size
    assert resp['acl'] == gf.acl
    assert resp['authz'] == gf.authz
    # check properties from datamodel
    assert resp['file_name'] == gf.file_name
    assert resp['data_type'] == gf.data_type
    assert resp['file_format'] == gf.file_format


def test_update_no_version(client, indexd):
    """
    Test that existing genomic files are updated with correct schema

    This should not create a new version
    """
    resp = _new_genomic_file(client)
    orig_calls = indexd.put.call_count

    genomic_file = resp['results']
    body = genomic_file
    response = client.patch(url_for(GENOMICFILE_LIST_URL) + '/' + body['kf_id'],
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps(body))
    resp = json.loads(response.data.decode("utf-8"))

    # Updates were made to the three versions
    assert indexd.put.call_count == orig_calls + 3
    assert 'rev' not in indexd.put.call_args_list[0].json


def test_update(client, indexd, entities):
    """
    Test updating an existing genomic file

    This will should create a new version in indexd
    """

    resp = _new_genomic_file(client)
    orig_calls = indexd.post.call_count
    participant = resp['results']
    kf_id = participant.get('kf_id')
    orig_gf = GenomicFile.query.get(kf_id)
    orig_uuid = orig_gf.uuid
    orig_did = orig_gf.latest_did

    body = {
        'file_name': 'hg37.bam',
        'size': 23498
    }

    response = client.patch(url_for(GENOMICFILE_URL,
                                    kf_id=kf_id),
                            data=json.dumps(body),
                            headers={'Content-Type': 'application/json'})

    assert indexd.post.call_count == orig_calls + 1
    assert indexd.post.called_with(orig_gf.latest_did)

    assert response.status_code == 200

    resp = json.loads(response.data.decode("utf-8"))
    assert 'genomic_file' in resp['_status']['message']
    assert 'updated' in resp['_status']['message']

    # Test response
    gf = resp['results']
    assert gf['kf_id'] == kf_id
    assert gf['file_name'] == body['file_name']

    # Test database object
    gf = GenomicFile.query.get(kf_id)
    gf.merge_indexd()
    assert gf.file_name, body['file_name']
    assert gf.uuid == orig_uuid
    assert gf.latest_did != orig_did


def test_delete(client, indexd, entities):
    """
    Test deleting a participant by id
    """
    init = GenomicFile.query.count()

    r = _new_genomic_file(client)
    kf_id = r['results']['kf_id']

    response = client.delete(url_for(GENOMICFILE_URL,
                                     kf_id=kf_id),
                             headers={'Content-Type': 'application/json'})

    resp = json.loads(response.data.decode("utf-8"))

    assert 'genomic_file' in resp['_status']['message']
    assert 'deleted' in resp['_status']['message']
    assert GenomicFile.query.count() == init
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

    init = GenomicFile.query.count()

    r = _new_genomic_file(client)
    kf_id = r['results']['kf_id']

    response = client.delete(url_for(GENOMICFILE_URL,
                                     kf_id=kf_id),
                             headers={'Content-Type': 'application/json'})

    resp = json.loads(response.data.decode("utf-8"))

    assert indexd.delete.call_count == 1
    assert 'fake error message' in resp['_status']['message']
    assert GenomicFile.query.count() == init + 1


def test_filter_by_se(client, indexd):
    """
    Test get and filter genomic files by study_id and/or
    sequencing_experiment_id
    """
    ses, rgs, gfs, studies = _create_all_entities()

    # Create query
    se = SequencingExperiment.query.filter_by(external_id='study0-se1').first()

    assert len(se.genomic_files) == 2
    _ids = {'study0-gf0', 'study0-gf2'}
    for gf in se.genomic_files:
        assert gf.external_id in _ids

    # Send get request
    filter_params = {'sequencing_experiment_id': se.kf_id,
                     'study_id': studies[0].kf_id}
    qs = urlencode(filter_params)
    endpoint = '{}?{}'.format('/genomic-files', qs)
    response = client.get(endpoint)
    # Check response status code
    assert response.status_code == 200
    # Check response content
    response = json.loads(response.data.decode('utf-8'))
    assert 2 == response['total']
    assert 2 == len(response['results'])
    gfs = response['results']

    for gf in gfs:
        assert gf['external_id'] in _ids


def test_filter_by_rg(client, indexd):
    """
    Test get and filter genomic files by study_id and/or read_group_id
    """
    ses, rgs, gfs, studies = _create_all_entities()

    # Create query
    rg = ReadGroup.query.filter_by(external_id='study0-rg1').first()

    assert len(rg.genomic_files) == 2
    _ids = {'study0-gf0', 'study0-gf2'}
    for gf in rg.genomic_files:
        assert gf.external_id in _ids

    # Send get request
    filter_params = {'read_group_id': rg.kf_id,
                     'study_id': studies[0].kf_id}
    qs = urlencode(filter_params)
    endpoint = '{}?{}'.format('/genomic-files', qs)
    response = client.get(endpoint)
    # Check response status code
    assert response.status_code == 200
    # Check response content
    response = json.loads(response.data.decode('utf-8'))
    assert 2 == response['total']
    assert 2 == len(response['results'])
    gfs = response['results']

    for gf in gfs:
        assert gf['external_id'] in _ids


def test_filter_by_bs(client, indexd):
    """
    Test get and filter genomic files by biospecimen_id
    """
    ses, rgs, gfs, studies = _create_all_entities()
    bs = Biospecimen.query.filter_by(external_sample_id='b0').first()
    s = Study.query.filter_by(external_id='s0').first()

    assert len(bs.genomic_files) == 1
    assert bs.genomic_files[0].external_id == 'study0-gf0'

    # Send get request
    filter_params = {'biospecimen_id': bs.kf_id}
    qs = urlencode(filter_params)
    endpoint = '{}?{}'.format('/genomic-files', qs)
    response = client.get(endpoint)
    # Check response status code
    assert response.status_code == 200
    # Check response content
    response = json.loads(response.data.decode('utf-8'))
    assert 1 == response['total']
    assert 1 == len(response['results'])
    gfs = response['results']
    _ids = {'study0-gf0'}
    for gf in gfs:
        assert gf['external_id'] in _ids

    # test study_id filter
    filter_params = {'study_id': s.kf_id}
    qs = urlencode(filter_params)
    endpoint = '{}?{}'.format('/biospecimens', qs)
    endpoint = '{}?{}'.format('/genomic-files', qs)
    response = client.get(endpoint)
    # Check response status code
    assert response.status_code == 200
    # Check response content
    response = json.loads(response.data.decode('utf-8'))
    assert 3 == response['total']
    assert 3 == len(response['results'])
    gfs = response['results']
    _ids = {'study0-gf0', 'study0-gf1', 'study0-gf2'}
    for gf in gfs:
        assert gf['external_id'] in _ids

    # Send get request
    filter_params = {'biospecimen_id': bs.kf_id,
                     'study_id': s.kf_id}
    qs = urlencode(filter_params)
    endpoint = '{}?{}'.format('/genomic-files', qs)
    response = client.get(endpoint)
    # Check response status code
    assert response.status_code == 200
    # Check response content
    response = json.loads(response.data.decode('utf-8'))
    assert 1 == response['total']
    assert 1 == len(response['results'])
    gfs = response['results']
    _ids = {'study0-gf0'}
    for gf in gfs:
        assert gf['external_id'] in _ids


def test_access_urls(client):
    """
    The access_urls field should be a field derived from the urls replacing
    s3 locations with gen3 http locations
    """
    ses, rgs, gfs, studies = _create_all_entities()
    gf = list(gfs.values())[0][0]
    gf = client.get(f'/genomic-files/{gf.kf_id}').json['results']
    assert gf['access_urls'] == [f'gen3/data/{gf["latest_did"]}',
                                 f'https://gen3.something.com/did']


def _new_genomic_file(client):
    """ Creates a genomic file """
    body = {
        'external_id': 'genomic_file_0',
        'file_name': 'hg38.bam',
        'size': 123,
        'data_type': 'Aligned Reads',
        'file_format': 'bam',
        'urls': ['s3://bucket/key'],
        'hashes': {'md5': 'd418219b883fce3a085b1b7f38b01e37'},
        'availability': 'Immediate Download',
        'controlled_access': False
    }

    response = client.post(url_for(GENOMICFILE_LIST_URL),
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(body))
    resp = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 201
    return resp


def _create_all_entities():
    """
    Create 2 studies with genomic files and read groups
    """
    sc = SequencingCenter(name='sc')
    studies = []
    ses = {}
    rgs = {}
    gfs = {}
    for j in range(2):
        s = Study(external_id='s{}'.format(j))
        p = Participant(external_id='p{}'.format(j))
        s.participants.append(p)
        study_gfs = gfs.setdefault('study{}'.format(j), [])
        for i in range(3):
            b = Biospecimen(external_sample_id='b{}'.format(i),
                            analyte_type='DNA',
                            sequencing_center=sc,
                            participant=p)
            gf = GenomicFile(
                external_id='study{}-gf{}'.format(j, i),
                urls=['s3://mybucket/key', 'https://gen3.something.com/did'],
                hashes={'md5': 'd418219b883fce3a085b1b7f38b01e37'})
            study_gfs.append(gf)
            b.genomic_files.append(gf)

        study_rgs = rgs.setdefault('study{}'.format(j), [])
        rg0 = ReadGroup(external_id='study{}-rg0'.format(j))
        rg0.genomic_files.extend(study_gfs[0:2])
        rg1 = ReadGroup(external_id='study{}-rg1'.format(j))
        rg1.genomic_files.extend([study_gfs[0],
                                  study_gfs[-1]])

        study_ses = ses.setdefault('study{}'.format(j), [])
        se0 = SequencingExperiment(external_id='study{}-se0'.format(j),
                                   experiment_strategy='WGS',
                                   is_paired_end=True,
                                   platform='platform',
                                   sequencing_center=sc)
        se0.genomic_files.extend(study_gfs[0:2])
        se1 = SequencingExperiment(external_id='study{}-se1'.format(j),
                                   experiment_strategy='WGS',
                                   is_paired_end=True,
                                   platform='platform',
                                   sequencing_center=sc)
        se1.genomic_files.extend([study_gfs[0],
                                  study_gfs[-1]])

        study_rgs.extend([rg0, rg1])
        study_ses.extend([se0, se1])
        studies.append(s)

    db.session.add_all(studies)
    db.session.commit()

    return ses, rgs, gfs, studies
