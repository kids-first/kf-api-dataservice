import json
import pytest
from dateutil import parser
from datetime import datetime
from urllib import parse
import uuid

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.investigator.models import Investigator
from dataservice.api.participant.models import Participant
from dataservice.api.family.models import Family
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sample.models import Sample
from dataservice.api.sample_relationship.models import SampleRelationship
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.read_group.models import (
    ReadGroup,
    ReadGroupGenomicFile
)
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.utils import iterate_pairwise
from dataservice.api.study_file.models import StudyFile
from dataservice.api.cavatica_app.models import CavaticaApp
from dataservice.api.task.models import (
    Task,
    TaskGenomicFile
)

from unittest.mock import MagicMock, patch
from tests.mocks import MockIndexd
from tests.conftest import ENDPOINTS, MAX_PAGE_LIMIT, DEFAULT_PAGE_LIMIT

pytest_plugins = ['tests.mocks']


class TestPagination:
    """
    Test that entities are iterated and returned properly
    """

    @pytest.fixture(scope='module')
    def participants(client):

        # Add a bunch of studies for pagination
        for i in range(MAX_PAGE_LIMIT + 1):
            params = {
                'external_id': f'Study_{i}',
                'short_code': f'KF_{i}'
            }
            s = Study(**params)
            db.session.add(s)

        for i in range(MAX_PAGE_LIMIT + 1):
            ca = CavaticaApp(name='app', revision=0)
            db.session.add(ca)

        # Add a bunch of study files
        s0 = Study.query.filter_by(external_id='Study_0').one()
        s1 = Study.query.filter_by(external_id='Study_1').one()
        for i in range(MAX_PAGE_LIMIT+1):
            sf = StudyFile(file_name='blah', study_id=s0.kf_id)
            db.session.add(sf)

        # Add a bunch of investigators
        for _ in range(MAX_PAGE_LIMIT + 2):
            inv = Investigator(name='test')
            inv.studies.extend([s0, s1])
            db.session.add(inv)

        # Add a bunch of families
        families = []
        for i in range(MAX_PAGE_LIMIT + 1):
            families.append(Family(external_id='Family_{}'.format(i)))
        db.session.add_all(families)
        db.session.flush()

        participants = []
        f0 = Family.query.filter_by(external_id='Family_0').one()
        f1 = Family.query.filter_by(external_id='Family_1').one()
        seq_cen = None
        for i in range(MAX_PAGE_LIMIT + 2):
            f = f0 if i < int(MAX_PAGE_LIMIT/2) else f1
            s = s0 if i < int(MAX_PAGE_LIMIT/2) else s1
            data = {
                'external_id': "test",
                'is_proband': True,
                'race': 'Asian',
                'ethnicity': 'Hispanic or Latino',
                'diagnosis_category': 'Cancer',
                'gender': 'Male'
            }
            p = Participant(**data, study_id=s.kf_id, family_id=f.kf_id)
            diag = Diagnosis()
            p.diagnoses = [diag]
            outcome = Outcome()
            p.outcomes = [outcome]
            phen = Phenotype()
            p.phenotypes = [phen]
            sample = Sample(external_id="sample-{i}")
            p.samples = [sample]
            participants.append(p)
            db.session.add(p)
            db.session.flush()

            seq_data = {
                'external_id': 'Seq_0',
                'experiment_strategy': 'WXS',
                'library_name': 'Test_library_name_1',
                'library_strand': 'Unstranded',
                'is_paired_end': False,
                'platform': 'Test_platform_name_1'
            }
            gf_kwargs = {
                'external_id': 'gf_0',
                'file_name': 'hg38.fq',
                'data_type': 'Aligned Reads',
                'file_format': 'fastq',
                'size': 1000,
                'urls': ['s3://bucket/key'],
                'hashes': {'md5': str(uuid.uuid4())},
                'controlled_access': False
            }
            seq_cen = SequencingCenter.query.filter_by(name="Baylor")\
                .one_or_none()
            if seq_cen is None:
                seq_cen = SequencingCenter(external_id='SC_0', name="Baylor")
                db.session.add(seq_cen)
                db.session.flush()
            seq_exp = SequencingExperiment(**seq_data,
                                           sequencing_center_id=seq_cen.kf_id)
            db.session.add(seq_exp)

            sample = p.samples[0]
            samp = Biospecimen(analyte_type='an analyte',
                               sequencing_center_id=seq_cen.kf_id,
                               participant=p, sample=sample
                               )
            p.biospecimens = [samp]
            db.session.add(samp)

            gf = GenomicFile(**gf_kwargs)
            db.session.add(gf)
            samp.genomic_files.append(gf)
            samp.diagnoses.append(diag)

            db.session.flush()

            rg = ReadGroup(lane_number=4,
                           flow_cell='FL0123')
            rg.genomic_files.append(gf)

            seq_exp.genomic_files.append(gf)

            ct = Task(name='task_{}'.format(i))
            ct.genomic_files.append(gf)
            ca.tasks.append(ct)

            db.session.flush()

        # Family relationships
        for participant1, participant2 in iterate_pairwise(participants):
            gender = participant1.gender
            rel = 'mother'
            if gender == 'male':
                rel = 'father'
            r = FamilyRelationship(participant1=participant1,
                                   participant2=participant2,
                                   participant1_to_participant2_relation=rel)
            db.session.add(r)

        # Sample relationships
        for p1, p2 in iterate_pairwise(participants):
            # Biologically incorrect, but done for testing only
            parent = p1.samples[0]
            child = p2.samples[0]
            r = SampleRelationship(
                parent=parent,
                child=child,
                external_parent_id=parent.external_id,
                external_child_id=child.external_id,
            )
            db.session.add(r)

        db.session.commit()

    @pytest.mark.parametrize('endpoint, expected_total', [
        ('/participants', int(MAX_PAGE_LIMIT/2)),
        ('/study-files', MAX_PAGE_LIMIT+1),
        ('/investigators', 1),
        ('/samples', int(MAX_PAGE_LIMIT/2)),
        ('/biospecimens', int(MAX_PAGE_LIMIT/2)),
        ('/sequencing-experiments', int(MAX_PAGE_LIMIT/2)),
        ('/diagnoses', int(MAX_PAGE_LIMIT/2)),
        ('/outcomes', int(MAX_PAGE_LIMIT/2)),
        ('/phenotypes', int(MAX_PAGE_LIMIT/2)),
        ('/families', 1),
        ('/family-relationships', int(MAX_PAGE_LIMIT/2)),
        ('/genomic-files', int(MAX_PAGE_LIMIT/2)),
        ('/read-groups', int(MAX_PAGE_LIMIT/2)),
        ('/sequencing-centers', 1),
        ('/cavatica-apps', 1),
        ('/tasks', int(MAX_PAGE_LIMIT/2)),
        ('/task-genomic-files', int(MAX_PAGE_LIMIT/2)),
        ('/read-group-genomic-files', int(MAX_PAGE_LIMIT/2)),
        ('/sequencing-experiment-genomic-files', int(MAX_PAGE_LIMIT/2)),
        ('/biospecimen-genomic-files', int(MAX_PAGE_LIMIT/2)),
        ('/biospecimen-diagnoses', int(MAX_PAGE_LIMIT/2))
    ])
    def test_study_filter(self, client, participants,
                          endpoint, expected_total):
        """
        Test pagination of resources with a study filter
        """
        s = Study.query.filter_by(external_id='Study_0').one()
        endpoint = '{}?study_id={}'.format(endpoint, s.kf_id)
        resp = client.get(endpoint)
        resp = json.loads(resp.data.decode('utf-8'))
        assert len(resp['results']) == min(expected_total, DEFAULT_PAGE_LIMIT)
        assert resp['limit'] == DEFAULT_PAGE_LIMIT
        assert resp['total'] == expected_total

        ids_seen = []
        # Iterate through via the `next` link
        while 'next' in resp['_links']:
            # Check formatting of next link
            self._check_link(resp['_links']['next'], {'study_id': s.kf_id})
            # Stash all the ids on the page
            ids_seen.extend([r['kf_id'] for r in resp['results']])
            resp = client.get(resp['_links']['next'])
            resp = json.loads(resp.data.decode('utf-8'))
            # Check formatting of the self link
            self._check_link(resp['_links']['self'], {'study_id': s.kf_id})

        ids_seen.extend([r['kf_id'] for r in resp['results']])
        assert len(ids_seen) == resp['total']

    @pytest.mark.parametrize('endpoint', [
        (ept) for ept in ENDPOINTS if ept != '/studies'
    ])
    def test_non_exist_study_filter(self, client, participants,
                                    endpoint):
        """
        Test pagination of resources with a study filter that doesn't exist or
        is invalid

        Should return no results
        """
        endpoint = '{}?study_id={}'.format(endpoint, 'SD_00000000')
        resp = client.get(endpoint)
        resp = json.loads(resp.data.decode('utf-8'))

        assert len(resp['results']) == 0
        assert resp['limit'] == DEFAULT_PAGE_LIMIT
        assert resp['total'] == 0

    @pytest.mark.parametrize('study_id', ['blah', 3489, 'PT_00001111'])
    @pytest.mark.parametrize('endpoint', [
        (ept) for ept in ENDPOINTS if ept != '/studies'
    ])
    def test_invalid_study_filter(self, client, participants,
                                  endpoint, study_id):
        """
        Test pagination of resources with a study filter that doesn't exist or
        is invalid

        Should return no results
        """
        endpoint = '{}?study_id={}'.format(endpoint, study_id)
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 400
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert ('could not retrieve entities:' in
                resp['_status']['message'])
        assert 'Invalid kf_id' in resp['_status']['message']
        assert 'study_id' in resp['_status']['message']

    @pytest.mark.parametrize('endpoint, expected_total', [
        ('/studies', MAX_PAGE_LIMIT+1),
        ('/investigators', MAX_PAGE_LIMIT+2),
        ('/participants', MAX_PAGE_LIMIT+2),
        ('/outcomes', MAX_PAGE_LIMIT+2),
        ('/biospecimens', MAX_PAGE_LIMIT+2),
        ('/samples', MAX_PAGE_LIMIT+2),
        ('/phenotypes', MAX_PAGE_LIMIT+2),
        ('/diagnoses', MAX_PAGE_LIMIT+2),
        ('/family-relationships', MAX_PAGE_LIMIT+1),
        ('/study-files', MAX_PAGE_LIMIT+1),
        ('/families', MAX_PAGE_LIMIT+1),
        ('/read-groups', MAX_PAGE_LIMIT+2),
        ('/sequencing-centers', 1),
        ('/cavatica-apps', MAX_PAGE_LIMIT+1),
        ('/tasks', MAX_PAGE_LIMIT+2),
        ('/task-genomic-files', MAX_PAGE_LIMIT+2),
        ('/read-group-genomic-files', MAX_PAGE_LIMIT+2),
        ('/sequencing-experiment-genomic-files', MAX_PAGE_LIMIT+2),
        ('/biospecimen-genomic-files', MAX_PAGE_LIMIT+2),
        ('/biospecimen-diagnoses', MAX_PAGE_LIMIT+2)
    ])
    def test_pagination(self, client, participants, endpoint, expected_total):
        """ Test pagination of resource """
        print("********************")
        print(Sample.query.count())
        resp = client.get(endpoint)
        resp = json.loads(resp.data.decode('utf-8'))

        assert len(resp['results']) == min(expected_total, DEFAULT_PAGE_LIMIT)
        assert resp['limit'] == DEFAULT_PAGE_LIMIT
        assert resp['total'] == expected_total

        ids_seen = []
        # Iterate through via the `next` link
        while 'next' in resp['_links']:
            # Check formatting of next link
            self._check_link(resp['_links']['next'], {})
            # Stash all the ids on the page
            ids_seen.extend([r['kf_id'] for r in resp['results']])
            resp = client.get(resp['_links']['next'])
            resp = json.loads(resp.data.decode('utf-8'))
            # Check formatting of the self link
            self._check_link(resp['_links']['self'], {})

        ids_seen.extend([r['kf_id'] for r in resp['results']])
        assert len(ids_seen) == resp['total']

    def test_same_created_at(self, client):
        """
        Test that many objects with the same created_at time may still be
        paginated correctly
        """
        created_at = datetime.now()
        studies = [Study(external_id=f'Study_{i}', short_code=f'KF-ST{i}')
                   for i in range(int(MAX_PAGE_LIMIT/2))]
        db.session.add_all(studies)
        db.session.flush()
        for study in studies:
            study.created_at = created_at
        db.session.flush()

        resp = client.get('/studies')
        resp = json.loads(resp.data.decode('utf-8'))
        ids_seen = []
        # Iterate through via the `next` link
        while 'next' in resp['_links']:
            ids_seen.extend([r['kf_id'] for r in resp['results']])
            resp = client.get(resp['_links']['next'])
            resp = json.loads(resp.data.decode('utf-8'))

        ids_seen.extend([r['kf_id'] for r in resp['results']])
        assert len(ids_seen) == Study.query.count()

    @pytest.mark.parametrize('endpoint', [
        (ept) for ept in ENDPOINTS
    ])
    def test_limit(self, client, participants, endpoint):
        # Check that limit param operates correctly
        response = client.get(endpoint + '?limit=5')
        response = json.loads(response.data.decode('utf-8'))
        if '/sequencing-centers' in endpoint:
            assert len(response['results']) == 1
        else:
            assert len(response['results']) == 5
        assert response['limit'] == 5

        response = client.get(endpoint + f'?limit={MAX_PAGE_LIMIT * 2}')
        response = json.loads(response.data.decode('utf-8'))
        if '/sequencing-centers' in endpoint:
            assert len(response['results']) == 1
        else:
            assert len(response['results']) == MAX_PAGE_LIMIT

        # Check unexpected limit param uses default
        response = client.get(endpoint + '?limit=dog')
        response = json.loads(response.data.decode('utf-8'))
        if '/sequencing-centers' in endpoint:
            assert len(response['results']) == 1
        else:
            assert len(response['results']) == DEFAULT_PAGE_LIMIT
        assert response['limit'] == DEFAULT_PAGE_LIMIT

    @pytest.mark.parametrize('endpoint', [
        (ept) for ept in ENDPOINTS
    ])
    def test_after(self, client, participants, endpoint):
        """ Test `after` offeset paramater """
        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        first = response['results'][0]['created_at']

        # Check unexpected after param returns the earliest
        response = client.get(endpoint + '?after=dog')
        response = json.loads(response.data.decode('utf-8'))
        assert response['results'][0]['created_at'] == first
        assert response['_links']['self'] == endpoint

        # Check that future dates return no results
        response = client.get(endpoint + '?after=2100-01-01')
        response = json.loads(response.data.decode('utf-8'))
        assert response['results'] == []

        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        ts = parser.parse(response['results'][-1]['created_at']).timestamp()

    @pytest.mark.parametrize('endpoint', [
        (ept) for ept in ENDPOINTS
    ])
    def test_self(self, client, participants, endpoint):
        """ Test that the self link gives the same page """
        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        if 'next' in response['_links']:
            next_page = response['_links']['next']

            response = client.get(next_page)
            response = json.loads(response.data.decode('utf-8'))
            results = response['results']

            response = client.get(response['_links']['self'])
            response = json.loads(response.data.decode('utf-8'))
            assert results == response['results']

    @pytest.mark.parametrize('endpoint', [
        (ept) for ept in ENDPOINTS
    ])
    def test_individual_links(self, client, participants, endpoint):
        """ Test that each individual result has properly formatted _links """
        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        results = response['results']

        for result in results:
            assert '_links' in result
            self_link = result['_links']
            response = client.get(result['_links']['self'])
            assert response.status_code == 200
            response = json.loads(response.data.decode('utf-8'))
            assert response['_status']['code'] == 200
            # Should only return the single entity
            assert isinstance(response['results'], dict)
            assert result['kf_id'] == response['results']['kf_id']
            assert 'collection' in result['_links']

    def _check_link(self, link_str, params):
        res = parse.urlsplit(link_str)
        q_params = parse.parse_qs(res.query)
        assert 'after' in q_params
        assert 'after_uuid' in q_params
        if 'study_id' in params:
            assert 'study_id' in q_params
        after_date = q_params.get('after')[0]
        after_uuid = q_params.get('after_uuid')[0]
        assert uuid.UUID(after_uuid)
        assert isinstance(datetime.fromtimestamp(float(after_date)), datetime)
        for k, v in params.items():
            assert q_params.get(k)[0] == v
