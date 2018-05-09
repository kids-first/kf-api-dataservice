import pytest
import json
import uuid
from dateutil import parser, tz
from datetime import datetime
from urllib.parse import urlencode

from pprint import pprint

from dataservice.extensions import db
from dataservice.utils import iterate_pairwise
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
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.study_file.models import StudyFile
from dataservice.api.cavatica_app.models import CavaticaApp
from dataservice.api.cavatica_task.models import (
    CavaticaTask,
    CavaticaTaskGenomicFile
)

# pytest_plugins = ['tests.mocks']

ENTITY_TOTAL = 15
SAMPLE_DATE = str(datetime.now().replace(tzinfo=tz.tzutc()))

ENTITY_ENDPOINT_MAP = {
    Study: '/studies',
    Investigator: '/investigators',
    StudyFile: '/study-files',
    Family: '/families',
    # FamilyRelationship: '/family-relationships',
    CavaticaApp: '/cavatica-apps',
    SequencingCenter: '/sequencing-centers',
    Participant: '/participants',
    Diagnosis: '/diagnoses',
    Phenotype: '/phenotypes',
    Outcome: '/outcomes',
    Biospecimen: '/biospecimens',
    GenomicFile: '/genomic-files',
    SequencingExperiment: '/sequencing-experiments',
    CavaticaTask: '/cavatica-tasks'
    # CavaticaTaskGenomicFile: '/cavatica-task-genomic-files'
}

ENTITY_PARAMS = {
    'fields': {
        '/studies': {'external_id': 'Study_0'},
        '/investigators': {'name': 'Investigator_0'},
        '/study-files': {'file_name': 'File_0'},
        '/cavatica-apps': {'name': 'App_0'},
        '/families': {'external_id': 'Family_0'},
        '/sequencing-centers': {'name': ''},
        '/participants': {
            'is_proband': True,
            'consent_type': 'GRU-IRB',
            'race': 'asian',
            'ethnicity': 'not hispanic',
            'gender': 'male'
        },
        '/biospecimens': {'analyte_type': 'DNA',
                          'external_sample_id': 'Biospecimen_0'},
        '/diagnoses': {'diagnosis_category': 'birth defect',
                       'source_text_diagnosis': 'Diagnosis_0'},
        '/outcomes': {'external_id': 'Outcome_0',
                      'vital_status': 'alive'},
        '/phenotypes': {'external_id': 'Phenotype_0'},
        '/sequencing-experiments': {
            'external_id': 'SeqExp_0',
            'experiment_strategy': 'WXS',
            'library_name': 'Library_1',
            'library_strand': 'Unstranded',
            'is_paired_end': False,
            'platform': 'Platform_0'
        },
        '/genomic-files': {
            'external_id': 'GenomicFile_0',
            'file_name': 'hg38.fq',
            'data_type': 'reads',
            'file_format': 'fastq',
            'size': 1000,
            'urls': ['s3://bucket/key'],
            'hashes': {'md5': str(uuid.uuid4())},
            'controlled_access': False
        },
        '/cavatica-tasks': {'name': 'CavaticaTask_0'}

    },
    'filter_params': {
        '/studies': {
            'valid': {
                'external_id': 'Study_1'
            },
            'invalid': []
        },
        '/investigators': {
            'valid': {
                'name': 'Investigator_1'
            }
        },
        '/study-files': {
            'valid': {
                'file_name': 'File_1'
            },
            'invalid': []
        },
        '/sequencing-centers': {
            'valid': {
                'name': ''
            }
        },
        '/cavatica-apps': {
            'valid': {
                'name': 'App_1'
            }
        },
        '/families': {
            'valid': {
                'external_id': 'Family_1'
            },
            'invalid': []
        },
        '/participants': {
            'valid': {
                'is_proband': False,
                'gender': 'female'
            },
            'invalid': [
                {'is_proband': 'hello'}
            ]
        },
        '/biospecimens': {
            'valid': {
                'analyte_type': 'RNA'
            },
            'invalid': [
                {'age_at_event_days': -1},
                {'age_at_event_days': 'hello'}
            ]
        },
        '/diagnoses': {
            'valid': {
                'diagnosis_category': 'cancer',
                'source_text_diagnosis': 'Diagnosis_1',
                'age_at_event_days': 100
            },
            'invalid': [
                {'age_at_event_days': -1},
                {'age_at_event_days': 'hello'},
            ]
        },
        '/outcomes': {
            'valid': {
                'external_id': 'Outcome_1',
                'vital_status': 'dead'
            },
            'invalid': [
                {'age_at_event_days': -1},
                {'age_at_event_days': 'hello'},
            ]
        },
        '/phenotypes': {
            'valid': {
                'external_id': 'Phenotype_1'
            },
            'invalid': [
                {'age_at_event_days': -1},
                {'age_at_event_days': 'hello'},
            ]
        },
        '/sequencing-experiments': {
            'valid': {
                'external_id': 'SeqExp_1',
                'is_paired_end': True
            }
        },
        '/genomic-files': {
            'valid': {
                'external_id': 'GenomicFile_1'
            }
        },
        '/cavatica-tasks': {
            'valid': {
                'name': 'CavaticaTask_1'
            }
        }
    }
}


class TestFilterParams:
    """
    Test filtering on pagnation endpoints
    """

    @pytest.fixture(scope='module')
    def entities(client):
        # Create initial entities
        with db.session.no_autoflush:
            entities = {}
            for model, endpoint in ENTITY_ENDPOINT_MAP.items():
                for i in range(ENTITY_TOTAL):
                    data = ENTITY_PARAMS['fields'][endpoint].copy()
                    if i % 2 != 0:
                        if endpoint in ENTITY_PARAMS['filter_params']:
                            data.update(ENTITY_PARAMS.get(
                                'filter_params')[endpoint]['valid'])
                    if model == Participant:
                        data['external_id'] = 'Participant_{}'.format(i)
                    if model == SequencingCenter:
                        data['name'] = 'SequencingCenter_{}'.format(i)
                    m = model(**data)
                    if model not in entities:
                        entities[model] = []
                    entities[model].append(m)

                    db.session.add(m)

            # Family relationships
            for participant, relative in iterate_pairwise(
                    entities[Participant]):
                gender = participant.gender
                rel = 'mother'
                if gender == 'male':
                    rel = 'father'
                r = FamilyRelationship(participant=participant,
                                       relative=relative,
                                       participant_to_relative_relation=rel)
                db.session.add(r)

            # Add relations
            s0 = entities[Study][0]
            f0 = entities[Family][0]
            p0 = entities[Participant][0]
            sc0 = entities[SequencingCenter][0]
            se0 = entities[SequencingExperiment][0]
            ca0 = entities[CavaticaApp][0]

            # Investigator
            for inv in entities[Investigator]:
                inv.studies.append(s0)
            # Study file
            for sf in entities[StudyFile]:
                sf.study = s0
            # Participant
            for ent in entities[Participant]:
                ent.study = s0
                ent.family = f0

            # Biospecimen, Diagnosis, Phenotype, Outcome
            participant_ents = [Biospecimen, Diagnosis, Phenotype, Outcome]
            for participant_ent in participant_ents:
                for ent in entities[participant_ent]:
                    ent.participant = p0
                    if Biospecimen == participant_ent:
                        ent.sequencing_center = sc0
            # SequencingExperiment
            for ent in entities[SequencingExperiment]:
                ent.sequencing_center = sc0

            # GenomicFiles
            bs0 = entities[Biospecimen][0]
            for ent in entities[GenomicFile]:
                ent.sequencing_experiment = se0
                ent.biospecimen = bs0

            # CavaticaTask
            for ent in entities[CavaticaApp]:
                ent.cavatica_app = ca0

            db.session.commit()

    @pytest.mark.parametrize('model',
                             [
                                 (Study),
                                 (StudyFile),
                                 (Participant),
                                 (Family),
                                 (Diagnosis),
                                 (Phenotype),
                                 (Outcome)
                             ])
    def test_filter_params(self, client, entities, model):
        """
        Test retrieving entities given filter parameters
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]
        filter_params = ENTITY_PARAMS['filter_params'][endpoint]['valid']
        expected_total = model.query.filter_by(
            **filter_params).count()

        # Make query string
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 200
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert resp['limit'] == 10
        assert len(resp['results']) == min(expected_total, 10)
        assert resp['total'] == expected_total
        # All results have correct field values
        for result in resp['results']:
            for k, v in filter_params.items():
                assert result.get(k) == v

    @pytest.mark.parametrize('model',
                             [
                                 (Study),
                                 (StudyFile),
                                 (Participant),
                                 (Family),
                                 (Diagnosis),
                                 (Phenotype),
                                 (Outcome)
                             ])
    def test_invalid_filter_params(self, client, entities, model):
        """
        Test retrieving entities given invalid filter parameters
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]
        filter_params = ENTITY_PARAMS['filter_params'][endpoint]
        all_invalid_params = filter_params.get('invalid', None)

        for invalid_params in all_invalid_params:
            # Make query string
            qs = urlencode(invalid_params)
            endpoint = '{}?{}'.format(endpoint, qs)
            # Send request
            response = client.get(endpoint)

            # Check status code
            assert response.status_code == 400
            # Check content
            resp = json.loads(response.data.decode('utf-8'))
            assert ('could not retrieve entities:' in
                    resp['_status']['message'])
            for k, v in invalid_params.items():
                assert k in resp['_status']['message']

    @pytest.mark.parametrize('model',
                             [
                                 (Study),
                                 (StudyFile),
                                 (Participant),
                                 (Family),
                                 (Diagnosis),
                                 (Phenotype),
                                 (Outcome)
                             ])
    def test_unknown_filter_params(self, client, entities, model):
        """
        Test retrieving entities given filter parameters that don't exist on
        the entity
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]
        filter_params = {'blabbityboo': 'foo'}
        expected_total = model.query.count()

        # Make query string
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 200
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert resp['limit'] == 10
        assert len(resp['results']) == min(expected_total, 10)
        assert resp['total'] == expected_total

    @pytest.mark.parametrize('field', ['created_at', 'modified_at'])
    @pytest.mark.parametrize('model',
                             [
                                 (Study),
                                 (StudyFile),
                                 (Participant),
                                 (Family),
                                 (Diagnosis),
                                 (Phenotype),
                                 (Outcome)
                             ])
    def test_generated_date_filters(self, client, entities, model, field):
        """
        Test retrieving entities w created_at and modified_at filters
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]
        entity = model.query.first()
        filter_params = {field: self._datetime_string(getattr(entity, field))}

        # Get expected total
        expected_total = 1

        # Make query string
        qs = urlencode(filter_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 200
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert resp['limit'] == 10
        assert len(resp['results']) == min(expected_total, 10)
        assert resp['total'] == expected_total
        # All results have correct field values
        for result in resp['results']:
            for k, v in filter_params.items():
                d = parser.parse(v).replace(tzinfo=tz.tzutc())
                assert parser.parse(result.get(k)) == (d)

    @pytest.mark.parametrize('invalid_params', [{'created_at': 'hello'},
                                                {'created_at': 92374},
                                                {'modified_at': 'hello'},
                                                {'modified_at': 92374},
                                                ])
    @pytest.mark.parametrize('model',
                             [
                                 (Study),
                                 (StudyFile),
                                 (Participant),
                                 (Family),
                                 (Diagnosis),
                                 (Phenotype),
                                 (Outcome)
                             ])
    def test_invalid_gen_date_filters(self, client, entities, model,
                                      invalid_params):
        """
        Test retrieving entities w created_at and modified_at filters
        """
        # Setup
        endpoint = ENTITY_ENDPOINT_MAP[model]

        # Make query string
        qs = urlencode(invalid_params)
        endpoint = '{}?{}'.format(endpoint, qs)
        # Send request
        response = client.get(endpoint)

        # Check status code
        assert response.status_code == 400
        # Check content
        resp = json.loads(response.data.decode('utf-8'))
        assert ('could not retrieve entities:' in
                resp['_status']['message'])
        for k, v in invalid_params.items():
            assert k in resp['_status']['message']

    def _datetime_string(self, dt):
        return 'T'.join(str(dt).split(' ')).split('+')[0]
