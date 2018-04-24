import json
import pytest
from dateutil import parser
from pprint import pprint
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
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.utils import iterate_pairwise
from dataservice.api.study_file.models import StudyFile

pytest_plugins = ['tests.mocks']


class TestPagination:
    """
    Test that entities are iterated and returned properly
    """

    @pytest.fixture(scope='function')
    def participants(client, indexd):

        # Add a bunch of studies for pagination
        for i in range(101):
            s = Study(external_id='Study_{}'.format(i))
            db.session.add(s)
        db.session.commit()

        # Add a bunch of study files
        s0 = Study.query.filter_by(external_id='Study_0').one()
        s1 = Study.query.filter_by(external_id='Study_1').one()
        for i in range(101):
            sf = StudyFile(file_name='blah', study_id=s0.kf_id)
            db.session.add(sf)
        db.session.commit()

        # Add a bunch of investigators
        for _ in range(102):
            inv = Investigator(name='test')
            inv.studies.extend([s0, s1])
            db.session.add(inv)
        db.session.commit()

        # Add a bunch of families
        families = []
        for i in range(101):
            families.append(Family(external_id='Family_{}'.format(i)))
        db.session.add_all(families)
        db.session.commit()

        participants = []
        f0 = Family.query.filter_by(external_id='Family_0').one()
        f1 = Family.query.filter_by(external_id='Family_1').one()
        for i in range(102):
            f = f0 if i < 50 else f1
            s = s0 if i < 50 else s1
            data = {
                'external_id': "test",
                'is_proband': True,
                'consent_type': 'GRU-IRB',
                'race': 'asian',
                'ethnicity': 'not hispanic',
                'gender': 'male'
            }

            p = Participant(**data, study_id=s.kf_id, family_id=f.kf_id)
            bsp = Biospecimen(analyte_type='an analyte')
            se_kwargs = {
                'external_id': 'se1',
                'experiment_strategy': 'WGS',
                'center': 'Baylor',
                'is_paired_end': True,
                'platform': 'Illumina'
            }
            seq_exp = SequencingExperiment(**se_kwargs)
            gf_kwargs = {
                'file_name': 'hg38.fq',
                'data_type': 'reads',
                'file_format': 'fastq',
                'size': 1000,
                'urls': ['s3://bucket/key'],
                'hashes': {'md5': str(uuid.uuid4())},
                'controlled_access': False,
                'availability': 'availble for download'
            }
            gf = GenomicFile(**gf_kwargs)
            gf.biospecimen = bsp
            gf.sequencing_experiment = seq_exp
            p.biospecimens = [bsp]
            diag = Diagnosis()
            p.diagnoses = [diag]
            outcome = Outcome()
            p.outcomes = [outcome]
            phen = Phenotype()
            p.phenotypes = [phen]
            participants.append(p)
            db.session.add(p)
        db.session.commit()

        # Family relationships
        for participant, relative in iterate_pairwise(participants):
            gender = participant.gender
            rel = 'mother'
            if gender == 'male':
                rel = 'father'
            r = FamilyRelationship(participant=participant, relative=relative,
                                   participant_to_relative_relation=rel)
            db.session.add(r)
        db.session.commit()

    @pytest.mark.parametrize('endpoint, expected_total', [
        ('/participants', 50),
        ('/study-files', 101),
        ('/investigators', 1),
        ('/biospecimens', 50),
        ('/sequencing-experiments', 50),
        ('/diagnoses', 50),
        ('/outcomes', 50),
        ('/phenotypes', 50),
        ('/families', 1),
        ('/family-relationships', 50),
        ('/genomic-files', 50)
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

        assert len(resp['results']) == min(expected_total, 10)
        assert resp['limit'] == 10
        assert resp['total'] == expected_total

        ids_seen = []
        # Iterate through via the `next` link
        while 'next' in resp['_links']:
            # Check formatting of next link
            # assert float(resp['_links']['next'].split('=')[-1])
            self._check_link(resp['_links']['next'], {'study_id': s.kf_id})
            # Stash all the ids on the page
            ids_seen.extend([r['kf_id'] for r in resp['results']])
            resp = client.get(resp['_links']['next'])
            resp = json.loads(resp.data.decode('utf-8'))
            # Check formatting of the self link
            # assert float(resp['_links']['self'].split('=')[-1])
            self._check_link(resp['_links']['self'], {'study_id': s.kf_id})

        ids_seen.extend([r['kf_id'] for r in resp['results']])

        assert len(ids_seen) == resp['total']

    @pytest.mark.parametrize('study_id', ['blah', 'ST_00000000', 50])
    @pytest.mark.parametrize('endpoint', [
        ('/participants'),
        ('/study-files'),
        ('/investigators'),
        ('/biospecimens'),
        ('/sequencing-experiments'),
        ('/diagnoses'),
        ('/outcomes'),
        ('/phenotypes'),
        ('/families'),
        ('/family-relationships'),
        ('/genomic-files')
    ])
    def test_non_exist_study_filter(self, client, participants,
                                    endpoint, study_id):
        """
        Test pagination of resources with a study filter that doesn't exist or
        is invalid

        Should return no results
        """
        endpoint = '{}?study_id={}'.format(endpoint, study_id)
        resp = client.get(endpoint)
        resp = json.loads(resp.data.decode('utf-8'))

        assert len(resp['results']) == 0
        assert resp['limit'] == 10
        assert resp['total'] == 0

    @pytest.mark.parametrize('endpoint, expected_total', [
        ('/studies', 101),
        ('/investigators', 102),
        ('/participants', 102),
        ('/outcomes', 102),
        ('/phenotypes', 102),
        ('/diagnoses', 102),
        ('/family-relationships', 101),
        ('/study-files', 101),
        ('/families', 101)
    ])
    def test_pagination(self, client, participants, endpoint, expected_total):
        """ Test pagination of resource """
        resp = client.get(endpoint)
        resp = json.loads(resp.data.decode('utf-8'))

        assert len(resp['results']) == 10
        assert resp['limit'] == 10
        assert resp['total'] == expected_total

        ids_seen = []
        # Iterate through via the `next` link
        while 'next' in resp['_links']:
            # Check formatting of next link
            assert float(resp['_links']['next'].split('=')[-1])
            # Stash all the ids on the page
            ids_seen.extend([r['kf_id'] for r in resp['results']])
            resp = client.get(resp['_links']['next'])
            resp = json.loads(resp.data.decode('utf-8'))
            # Check formatting of the self link
            assert float(resp['_links']['self'].split('=')[-1])

        ids_seen.extend([r['kf_id'] for r in resp['results']])

        assert len(ids_seen) == resp['total']

    @pytest.mark.parametrize('endpoint', [
        ('/studies'),
        ('/investigators'),
        ('/participants'),
        ('/outcomes'),
        ('/phenotypes'),
        ('/diagnoses'),
        ('/biospecimens'),
        ('/family-relationships'),
        ('/study-files'),
        ('/families')
    ])
    def test_limit(self, client, participants, endpoint):
        # Check that limit param operates correctly
        response = client.get(endpoint + '?limit=5')
        response = json.loads(response.data.decode('utf-8'))
        assert len(response['results']) == 5
        assert response['limit'] == 5

        response = client.get(endpoint + '?limit=200')
        response = json.loads(response.data.decode('utf-8'))
        assert len(response['results']) == 100

        # Check unexpected limit param uses default
        response = client.get(endpoint + '?limit=dog')
        response = json.loads(response.data.decode('utf-8'))
        assert len(response['results']) == 10
        assert response['limit'] == 10

    @pytest.mark.parametrize('endpoint', [
        ('/studies'),
        ('/investigators'),
        ('/participants'),
        ('/outcomes'),
        ('/phenotypes'),
        ('/diagnoses'),
        ('/biospecimens'),
        ('/family-relationships'),
        ('/study-files'),
        ('/families')
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
        ('/studies'),
        ('/investigators'),
        ('/participants'),
        ('/outcomes'),
        ('/phenotypes'),
        ('/diagnoses'),
        ('/biospecimens'),
        ('/family-relationships'),
        ('/study-files'),
        ('/families')
    ])
    def test_self(self, client, participants, endpoint):
        """ Test that the self link gives the same page """
        response = client.get(endpoint)
        response = json.loads(response.data.decode('utf-8'))
        next_page = response['_links']['next']

        response = client.get(next_page)
        response = json.loads(response.data.decode('utf-8'))
        results = response['results']

        response = client.get(response['_links']['self'])
        response = json.loads(response.data.decode('utf-8'))
        assert results == response['results']

    @pytest.mark.parametrize('endpoint', [
        ('/participants'),
        ('/outcomes'),
        ('/diagnoses'),
        ('/biospecimens'),
        ('/family-relationships'),
        ('/study-files'),
        ('/families')
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
        assert 'study_id' in q_params
        assert float(q_params.get('after')[0])
        for k, v in params.items():
            assert q_params.get(k)[0] == v
