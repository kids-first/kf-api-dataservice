import os
import json
from datetime import datetime
from dateutil import tz
import pytest

from dataservice import create_app
from dataservice.utils import iterate_pairwise, read_json
from dataservice.extensions import db
from dataservice.api.investigator.models import Investigator
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.family.models import Family
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.study_file.models import StudyFile
from dataservice.api.cavatica_app.models import CavaticaApp
from dataservice.api.cavatica_task.models import (
    CavaticaTask,
    CavaticaTaskGenomicFile
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
    SequencingExperiment: '/sequencing-experiments',
    CavaticaTask: '/cavatica-tasks',
    CavaticaTaskGenomicFile: '/cavatica-task-genomic-files'
}

ENDPOINT_ENTITY_MAP = {v: k for k, v in ENTITY_ENDPOINT_MAP.items()}
ENDPOINTS = list(ENTITY_ENDPOINT_MAP.values())


def _create_entity_params(filepath):
    # Read data from file
    data = read_json(filepath)
    # Apply overrides
    d = str(datetime.now().replace(tzinfo=tz.tzutc()))
    data['fields']['/biospecimens']['shipment_date'] = d
    data['fields']['/sequencing-experiments']['experiment_date'] = d
    data['filter_params']['/biospecimens']['valid']['shipment_date'] = d
    data['filter_params']['/sequencing-experiments']['valid']['experiment_date'] = d
    return data


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(ROOT_DIR, 'data.json')
ENTITY_PARAMS = _create_entity_params(DATA_FILE)


@pytest.yield_fixture(scope='session')
def app():
    yield create_app('testing')


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
    db.drop_all()


@pytest.yield_fixture(scope='function')
def swagger(client):
    yield json.loads(client.get('/swagger').data.decode('utf-8'))


@pytest.fixture(scope='module')
def entities(client):
    # Create initial entities
    with db.session.no_autoflush:
        _entities = {}
        for model, endpoint in ENTITY_ENDPOINT_MAP.items():
            if model in {FamilyRelationship,
                         CavaticaTaskGenomicFile}:
                continue
            for i in range(ENTITY_TOTAL):
                data = ENTITY_PARAMS['fields'][endpoint].copy()
                if i % 2 != 0:
                    if endpoint in ENTITY_PARAMS['filter_params']:
                        data.update(ENTITY_PARAMS.get(
                            'filter_params')[endpoint]['valid'])
                if model == Participant:
                    data['external_id'] = 'Participant_{}'.format(i)
                if model == SequencingCenter:
                    _name = 'SequencingCenter_{}'.format(i)
                    data['name'] = _name
                    ENTITY_PARAMS['fields']['/sequencing-centers'].update(
                        {'name': _name}
                    )
                m = model(**data)
                if model not in _entities:
                    _entities[model] = []
                _entities[model].append(m)

                db.session.add(m)

        # Family relationships
        for participant, relative in iterate_pairwise(
                _entities[Participant]):
            gender = participant.gender
            rel = 'mother'
            if gender == 'male':
                rel = 'father'
            r = FamilyRelationship(participant=participant,
                                   relative=relative,
                                   participant_to_relative_relation=rel)
            if model not in _entities:
                _entities[FamilyRelationship] = []
            _entities[FamilyRelationship].append(r)

            ENTITY_PARAMS['fields']['/family-relationships'].update({
                'participant_to_relative_relation': rel
            })

            db.session.add(r)

        # Cavatica task genomic files
        for i, (ct, gf) in enumerate(zip(
                _entities[CavaticaTask], _entities[GenomicFile])):
            is_input = True
            if i % 2 == 0:
                is_input = False
            ctgf = CavaticaTaskGenomicFile(cavatica_task=ct,
                                           genomic_file=gf,
                                           is_input=is_input)
            if model not in _entities:
                _entities[CavaticaTaskGenomicFile] = []
            _entities[CavaticaTaskGenomicFile].append(ctgf)

            ENTITY_PARAMS['fields']['/cavatica-task-genomic-files'].update({
                'is_input': is_input
            })

            db.session.add(ctgf)

        # Add relations
        s0 = _entities[Study][0]
        f0 = _entities[Family][0]
        p0 = _entities[Participant][0]
        sc0 = _entities[SequencingCenter][0]
        se0 = _entities[SequencingExperiment][0]
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

        # GenomicFiles
        bs0 = _entities[Biospecimen][0]
        for ent in _entities[GenomicFile]:
            ent.sequencing_experiment = se0
            ent.biospecimen = bs0

        # CavaticaTask
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
