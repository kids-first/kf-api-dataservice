import json
import pytest
import uuid

from dataservice import create_app
from dataservice.extensions import db
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.demographic.models import Demographic
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.sample.models import Sample
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_experiment.models import SequencingExperiment

from tests.mocks import MockIndexd


@pytest.yield_fixture(scope='module')
def app():
    return create_app('testing')


@pytest.yield_fixture(scope='session')
def app():
    yield create_app('testing')

@pytest.yield_fixture(scope='function')
def client(app):
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield app.test_client()
    # Need to make sure we close all connections so pg won't lock tables
    db.session.close()
    db.drop_all()


@pytest.yield_fixture(scope='function')
def swagger(client):
    yield json.loads(client.get('/swagger').data.decode('utf-8'))


@pytest.fixture
def entities(client, mocker):
    mock = mocker.patch('dataservice.api.genomic_file.models.requests')
    indexd = MockIndexd()
    mock.get = indexd.get
    mock.post = indexd.post
    """
    Create mock entities
    """
    inputs = {
        '/genomic-files': {
            'file_name': 'hg38.fq',
            'data_type': 'reads',
            'file_format': 'fastq',
            'file_url': 's3://bucket/key',
            'urls': ['s3://bucket/key'],
            'md5sum': str(uuid.uuid4()),
            'controlled_access': False
        },
        '/studies': {
            'external_id': 'phs001'
        },
        '/sequencing-experiment': {
            'external_id': 'WGS-01',
            'instrument_model': 'HiSeq',
            'experiment_strategy': 'WGS',
            'platform': 'illumina',
            'center': 'WashU',
            'is_paired_end': True
        },
        '/participants': {
            'external_id': 'p0',
            'is_proband': True,
            'family_id': 'family0',
            'consent_type': 'GRU-IRB'
        },
        '/demographics': {
            'race': 'black',
            'gender': 'male',
            'ethnicity': 'hispanic or latino'
        },
        '/samples': {
            'external_id': 's0',
            'tissue_type': 'tissue',
            'composition': 'comp',
            'anatomical_site': 'site',
            'age_at_event_days': 365,
            'tumor_descriptor': 'tumor'
        },
        '/aliquots': {
            'analyte_type': 'DNA'
        },
        '/diagnoses': {
            'external_id': 'd0',
            'diagnosis': 'diag',
            'age_at_event_days': 365
        },
        '/outcomes': {
            'vital_status': 'Alive',
            'disease_related': False,
            'age_at_event_days': 120,
        },
        '/phenotypes': {
            'phenotype': 'test phenotype 1',
            'hpo_id': 'HP:0000118',
            'age_at_event_days': 120
        }
    }

    # Create and save entities to db
    study = Study(**inputs['/studies'])
    p = Participant(**inputs['/participants'], study=study)
    demo = Demographic(**inputs['/demographics'], participant_id=p.kf_id)
    sample = Sample(**inputs['/samples'], participant_id=p.kf_id)
    diagnosis = Diagnosis(**inputs['/diagnoses'], participant_id=p.kf_id)
    aliquot = Aliquot(**inputs['/aliquots'])
    seq_experiment = SequencingExperiment(**inputs['/sequencing-experiment'])
    genomic_file = GenomicFile(**inputs['/genomic-files'])
    p.demographic = demo
    p.samples = [sample]
    sample.aliquots = [aliquot]
    aliquot.sequencing_experiments = [seq_experiment]
    seq_experiment.genomic_files = [genomic_file]
    p.diagnoses = [diagnosis]
    db.session.add(p)
    db.session.add(seq_experiment)
    db.session.commit()

    # Add foreign keys
    inputs['/participants']['study_id'] = study.kf_id
    endpoints = ['/demographics', '/diagnoses', '/samples', '/outcomes',
                 '/phenotypes']
    for e in endpoints:
        inputs[e]['participant_id'] = p.kf_id

    # Add kf_ids
    inputs['kf_ids'] = {'/participants': p.kf_id}

    inputs['/genomic-files']['sequencing_experiment_id']  = seq_experiment.kf_id

    return inputs
