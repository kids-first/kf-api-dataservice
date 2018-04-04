import json
import pytest
from dateutil import parser

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.investigator.models import Investigator
from dataservice.api.participant.models import Participant
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.sample.models import Sample
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.utils import iterate_pairwise
from dataservice.api.study_file.models import StudyFile


class TestPagination:
    """
    Test that entities are iterated and returned properly
    """

    @pytest.fixture(scope='module')
    def participants(client):

        # Add a bunch of studies for pagination
        for _ in range(101):
            s = Study(external_id='blah')
            sf = StudyFile(file_name='blah', study_id =s.kf_id)
            s.study_files.extend([sf])
            db.session.add(s)
        db.session.commit()

        # Add a bunch of investigators
        for _ in range(102):
            inv = Investigator(name='test')
            db.session.add(inv)
        db.session.commit()

        s = Study(external_id='blah', name='test')
        s.investigator = inv
        db.session.add(s)
        db.session.flush()
        participants = []
        for i in range(102):
            data = {
                'external_id': "test",
                'is_proband': True,
                'consent_type': 'GRU-IRB',
                'race': 'asian',
                'ethnicity': 'not hispanic',
                'gender': 'male'
            }
            p = Participant(**data, study_id=s.kf_id)
            se_kwargs = {
                'external_id': 'se1',
                'experiment_strategy': 'WGS',
                'center': 'Baylor',
                'is_paired_end': True,
                'platform': 'Illumina'
            }
            seq_exp = SequencingExperiment(**se_kwargs)
            aliquot = Aliquot(analyte_type='an analyte',
                              sequencing_experiments=[seq_exp])
            samp = Sample(aliquots=[aliquot])
            p.samples = [samp]
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
        ('/studies', 102),
        ('/investigators', 102),
        ('/participants', 102),
        ('/outcomes', 102),
        ('/phenotypes', 102),
        ('/diagnoses', 102),
        ('/samples', 102),
        ('/aliquots', 102),
        ('/sequencing-experiments', 102),
        ('/family-relationships', 101),
        ('/study-files',101)
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
        ('/samples'),
        ('/aliquots'),
        ('/sequencing-experiments'),
        ('/family-relationships'),
        ('/study-files')
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
        ('/samples'),
        ('/aliquots'),
        ('/sequencing-experiments'),
        ('/family-relationships'),
        ('/study-files')
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
        ('/samples'),
        ('/aliquots'),
        ('/sequencing-experiments'),
        ('/family-relationships'),
        ('/study-files')
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
        ('/samples'),
        ('/aliquots'),
        ('/sequencing-experiments'),
        ('/family-relationships'),
        ('/study-files')
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
