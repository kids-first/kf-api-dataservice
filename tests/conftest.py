import os
import json
from datetime import datetime
from dateutil import tz
from collections import defaultdict
import pytest

from dataservice import create_app
from dataservice.utils import iterate_pairwise, read_json
from dataservice.extensions import db
from dataservice.api.investigator.models import Investigator
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.family.models import Family
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile
)
from dataservice.api.biospecimen.models import BiospecimenDiagnosis
from dataservice.api.read_group.models import (
    ReadGroup,
    ReadGroupGenomicFile
)
from dataservice.api.sequencing_experiment.models import (
    SequencingExperiment,
    SequencingExperimentGenomicFile
)
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.study_file.models import StudyFile
from dataservice.api.cavatica_app.models import CavaticaApp
from dataservice.api.task.models import (
    Task,
    TaskGenomicFile
)
from unittest.mock import MagicMock, patch
from tests.mocks import MockIndexd
pytest_plugins = ['tests.mocks']

ENTITY_TOTAL = 15
ENTITY_ENDPOINT_MAP = {
    Study: '/studies',
    Investigator: '/investigators',
    StudyFile: '/study-files',
    Family: '/families',
    FamilyRelationship: '/family-relationships',
    CavaticaApp: '/cavatica-apps',
    SequencingCenter: '/sequencing-centers',
    Participant: '/participants',
    Diagnosis: '/diagnoses',
    Phenotype: '/phenotypes',
    Outcome: '/outcomes',
    Biospecimen: '/biospecimens',
    GenomicFile: '/genomic-files',
    BiospecimenGenomicFile: '/biospecimen-genomic-files',
    BiospecimenDiagnosis: '/biospecimen-diagnoses',
    ReadGroup: '/read-groups',
    SequencingExperiment: '/sequencing-experiments',
    Task: '/tasks',
    TaskGenomicFile: '/task-genomic-files',
    ReadGroupGenomicFile: '/read-group-genomic-files',
    SequencingExperimentGenomicFile: '/sequencing-experiment-genomic-files'
}

ENDPOINT_ENTITY_MAP = {v: k for k, v in ENTITY_ENDPOINT_MAP.items()}
ENDPOINTS = list(ENTITY_ENDPOINT_MAP.values())

DEFAULT_PAGE_LIMIT = 100
MAX_PAGE_LIMIT = 1000


def _create_entity_params(filepath):
    # Read data from file
    data = read_json(filepath)
    # Apply overrides
    d = str(datetime.now().replace(tzinfo=tz.tzutc()))
    data['fields']['/biospecimens']['shipment_date'] = d
    data['fields']['/sequencing-experiments']['experiment_date'] = d
    data['filter_params']['/biospecimens']['valid']['shipment_date'] = d
    data['filter_params']['/sequencing-experiments'][
        'valid']['experiment_date'] = d
    return data


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(ROOT_DIR, 'data.json')
ENTITY_PARAMS = _create_entity_params(DATA_FILE)


@pytest.yield_fixture(scope='session')
def app():
    yield create_app('testing')


@pytest.yield_fixture(scope='function')
def sns_topic(app):
    TOPIC_ARN = 'arn:aws:sns:*:123456789012:my_topic'
    app.config['SNS_EVENT_ARN'] = TOPIC_ARN
    yield create_app('testing')
    app.config['SNS_EVENT_ARN'] = None


@pytest.yield_fixture(scope='module')
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
    db.session.remove()
    db.drop_all()


@pytest.yield_fixture(scope='function')
def swagger(client):
    yield json.loads(client.get('/swagger').data.decode('utf-8'))


@pytest.fixture(scope='module')
def entities(client):
    return make_entities(client)


def make_entities(client):
    # Create initial entities
    with db.session.no_autoflush:
        _entities = defaultdict(list)
        for model, endpoint in ENTITY_ENDPOINT_MAP.items():
            if model in {FamilyRelationship,
                         TaskGenomicFile,
                         BiospecimenGenomicFile,
                         BiospecimenDiagnosis,
                         ReadGroupGenomicFile,
                         SequencingExperimentGenomicFile}:
                continue
            for i in range(ENTITY_TOTAL):
                data = ENTITY_PARAMS['fields'][endpoint].copy()
                if i % 2 != 0:
                    if endpoint in ENTITY_PARAMS['filter_params']:
                        data.update(ENTITY_PARAMS.get(
                            'filter_params')[endpoint]['valid'])
                if model == Participant:
                    data['external_id'] = 'Participant_{}'.format(i)
                if model == Study:
                    data['short_code'] = f'KF_ST{i}'
                if model == SequencingCenter:
                    _name = 'SequencingCenter_{}'.format(i)
                    data['name'] = _name
                    ENTITY_PARAMS['fields']['/sequencing-centers'].update(
                        {'name': _name}
                    )
                m = model(**data)
                _entities[model].append(m)

                db.session.add(m)

        # Family relationships
        for participant, participant2 in iterate_pairwise(
                _entities[Participant]):
            gender = participant.gender
            rel = 'mother'
            if gender == 'male':
                rel = 'father'
            r = FamilyRelationship(participant1=participant,
                                   participant2=participant2,
                                   participant1_to_participant2_relation=rel)
            if model not in _entities:
                _entities[FamilyRelationship] = []
            _entities[FamilyRelationship].append(r)

            ENTITY_PARAMS['fields']['/family-relationships'].update({
                'participant1_to_participant2_relation': rel
            })

            db.session.add(r)

        # Task genomic files
        for i, (ct, gf) in enumerate(zip(
                _entities[Task], _entities[GenomicFile])):
            is_input = True
            if i % 2 == 0:
                is_input = False
            ctgf = TaskGenomicFile(task=ct,
                                   genomic_file=gf,
                                   is_input=is_input)
            _entities[TaskGenomicFile].append(ctgf)

            ENTITY_PARAMS['fields']['/task-genomic-files'].update({
                'is_input': is_input
            })

            db.session.add(ctgf)

        # Biospecimen genomic files
        for i, (bs, gf) in enumerate(zip(
                _entities[Biospecimen], _entities[GenomicFile])):
            bsgf = BiospecimenGenomicFile(biospecimen=bs,
                                          genomic_file=gf)
            _entities[BiospecimenGenomicFile].append(bsgf)
            db.session.add(bsgf)

        # Read Group Genomic Files
        for i, (rg, gf) in enumerate(zip(
                _entities[ReadGroup], _entities[GenomicFile])):
            rggf = ReadGroupGenomicFile(read_group=rg,
                                        genomic_file=gf)
            _entities[ReadGroupGenomicFile].append(rggf)
            db.session.add(rggf)

        # Sequencing Experiment Genomic Files
        for i, (se, gf) in enumerate(
            zip(_entities[SequencingExperiment],
                _entities[GenomicFile])):
            segf = SequencingExperimentGenomicFile(sequencing_experiment=se,
                                                   genomic_file=gf)
            _entities[SequencingExperimentGenomicFile].append(segf)
            db.session.add(segf)

        # Biospecimen genomic files
        for i, (b, d) in enumerate(zip(_entities[Biospecimen],
                                       _entities[Diagnosis])):
            bd = BiospecimenDiagnosis(biospecimen=b,
                                      diagnosis=d)
            _entities[BiospecimenDiagnosis].append(bd)
            db.session.add(bd)

        # Add relations
        s0 = _entities[Study][0]
        f0 = _entities[Family][0]
        p0 = _entities[Participant][0]
        sc0 = _entities[SequencingCenter][0]
        ca0 = _entities[CavaticaApp][0]

        # Investigator
        for inv in _entities[Investigator]:
            inv.studies.append(s0)
        # Study file
        for sf in _entities[StudyFile]:
            sf.study = s0
        # Participant
        for ent in _entities[Participant]:
            ent.study = s0
            ent.family = f0

        # Biospecimen, Diagnosis, Phenotype, Outcome
        participant_ents = [Biospecimen, Diagnosis, Phenotype, Outcome]
        for participant_ent in participant_ents:
            for ent in _entities[participant_ent]:
                ent.participant = p0
                if Biospecimen == participant_ent:
                    ent.sequencing_center = sc0
        # SequencingExperiment
        for ent in _entities[SequencingExperiment]:
            ent.sequencing_center = sc0

        # Task
        for ent in _entities[CavaticaApp]:
            ent.cavatica_app = ca0

        db.session.commit()

    return _entities


def _add_foreign_keys(inputs, entity):
    from sqlalchemy.orm import (
        object_mapper,
        ColumnProperty
    )
    mapper = object_mapper(entity)
    for prop in mapper.iterate_properties:
        if isinstance(prop, ColumnProperty):
            attr = getattr(entity.__class__.__table__.c, prop.key)
            if attr.foreign_keys:
                value = getattr(entity, prop.key)
                if value:
                    inputs.update({prop.key: value})
    return inputs
