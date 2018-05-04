import json
from datetime import datetime
import pytest
import uuid

from dataservice import create_app
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

ENDPOINTS = [
    '/studies',
    '/investigators',
    '/participants',
    '/outcomes',
    '/phenotypes',
    '/diagnoses',
    '/biospecimens',
    '/sequencing-experiments',
    '/sequencing-centers',
    '/family-relationships',
    '/study-files',
    '/families',
    '/family-relationships',
    '/studies',
    '/investigators',
    '/outcomes',
    '/phenotypes',
    '/genomic-files',
    '/cavatica-tasks',
    '/cavatica-apps',
    '/cavatica-task-genomic-files'
]

pytest_plugins = ['tests.mocks']


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
def entities(client, indexd):
    """
    Create mock entities
    """
    inputs = {
        '/investigators': {
            'external_id': 'inv001',
            'name': 'submitter'
        },
        '/cavatica-task-genomic-files': {
            'is_input': True
        },
        '/cavatica-apps': {
            'external_cavatica_app_id': 'app1',
            'name': 'MyApp',
            'revision': 1,
            'github_commit_url': 'http://www.github.com'
        },
        '/cavatica-tasks': {
            'external_cavatica_task_id': str(uuid.uuid4()),
            'name': 'MyTask'
        },
        '/genomic-files': {
            'external_id': 'genfile001',
            'file_name': 'hg38.fq',
            'data_type': 'reads',
            'file_format': 'fastq',
            'size': 1000,
            'urls': ['s3://bucket/key'],
            'hashes': {'md5': str(uuid.uuid4())},
            'controlled_access': False,
            'acl': ['TEST01'],
            'availability': 'availble for download'
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
            'consent_type': 'GRU-IRB',
            'race': 'black',
            'gender': 'male',
            'ethnicity': 'hispanic or latino'
        },
        '/families': {
            'external_id': 'family0'
        },
        '/biospecimens': {
            'external_sample_id': 's0',
            'external_aliquot_id': 'a0',
            'source_text_tissue_type': 'tissue',
            'composition': 'comp',
            'source_text_anatomical_site': 'site',
            'age_at_event_days': 365,
            'source_text_tumor_descriptor': 'tumor',
            'shipment_origin': 'CORIELL',
            'analyte_type': 'DNA',
            'concentration_mg_per_ml': 200.0,
            'volume_ml': 13.99,
            'shipment_date': str(datetime.utcnow()),
            'uberon_id_anatomical_site': 'test',
            'spatial_descriptor': 'left side',
            'ncit_id_tissue_type': 'Test',
            'ncit_id_anatomical_site': 'C12439'
        },
        '/sequencing-experiments': {
            'external_id': 'se1',
            'experiment_date': str(datetime.utcnow()),
            'experiment_strategy': 'WGS',
            'library_name': 'a library',
            'library_strand': 'a strand',
            'is_paired_end': True,
            'platform': 'Illumina',
            'instrument_model': 'HiSeqX',
            'max_insert_size': 500,
            'mean_insert_size': 300,
            'mean_depth': 60.89,
            'total_reads': 1000,
            'mean_read_length': 50
        },
        '/diagnoses': {
            'external_id': 'd0',
            'source_text_diagnosis': 'diag',
            'age_at_event_days': 365,
            'mondo_id_diagnosis': 'DOID:8469',
            'icd_id_diagnosis': 'J10.01',
            'uberon_id_tumor_location': 'UBERON:0000955',
            'spatial_descriptor': 'left side'
        },
        '/outcomes': {
            'external_id': 'out001',
            'vital_status': 'Alive',
            'disease_related': 'False',
            'age_at_event_days': 120,
        },
        '/phenotypes': {
            'external_id': 'phe001',
            'source_text_phenotype': 'test phenotype 1',
            'hpo_id_phenotype': 'HP:0000118',
            'snomed_id_phenotype': '38033009',
            'age_at_event_days': 120
        },

        '/family-relationships': {
            'external_id': 'famrel001',
            'participant_to_relative_relation': 'mother'
        },
        '/study-files': {
            'external_id': 'studfile001',
            'file_name': 'test_file_name 1',
            'data_type': 'clinical',
            'file_format': 'csv',
            'availability': 'available for download',
            'size': 1000,
            'urls': ['s3://bucket/key'],
            'hashes': {'md5': str(uuid.uuid4())}
        },
        '/sequencing-centers': {
            'external_id': 'SC001',
            'name': 'Baylor'
        }
    }

    # Create and save entities to db
    # Study, investigator
    investigator = Investigator(**inputs['/investigators'])
    study = Study(**inputs['/studies'])
    study.investigator = investigator

    # Add participants to study
    sf = StudyFile(**inputs['/study-files'], study_id=study.kf_id)
    p = Participant(**inputs['/participants'])
    p1 = Participant(**inputs['/participants'])
    p2 = Participant(**inputs['/participants'])

    family = Family(**inputs['/families'])
    family.participants.extend([p1, p2])

    study.participants.extend([p, p1, p2])
    db.session.add(study)
    db.session.commit()

    # Add entities to participant
    outcome = Outcome(**inputs['/outcomes'], participant_id=p.kf_id)
    phenotype = Phenotype(**inputs['/phenotypes'], participant_id=p.kf_id)
    diagnosis = Diagnosis(**inputs['/diagnoses'], participant_id=p.kf_id)
    seq_center = SequencingCenter.query.\
        filter_by(name=inputs['/sequencing-centers']['name'])\
        .one_or_none()
    if seq_center is None:
        seq_center = SequencingCenter(**inputs['/sequencing-centers'])
        db.session.add(seq_center)
        db.session.commit()
    seq_exp = SequencingExperiment(**inputs['/sequencing-experiments'],
                                   sequencing_center_id=seq_center.kf_id)

    biospecimen = Biospecimen(**inputs['/biospecimens'],
                              participant_id=p.kf_id,
                              sequencing_center_id=seq_center.kf_id)
    gen_file = GenomicFile(**inputs['/genomic-files'],
                           biospecimen_id=biospecimen.kf_id,
                           sequencing_experiment_id=seq_exp.kf_id)
    ca = CavaticaApp(**inputs['/cavatica-apps'])
    ct = CavaticaTask(**inputs['/cavatica-tasks'],
                      cavatica_app=ca)
    ctgf = CavaticaTaskGenomicFile(cavatica_task=ct, genomic_file=gen_file,
                                   is_input=False)

    biospecimen.genomic_files = [gen_file]
    seq_exp.genomic_files = [gen_file]
    seq_center.sequencing_experiments = [seq_exp]
    seq_center.biospecimens = [biospecimen]
    p.biospecimens = [biospecimen]
    p.diagnoses = [diagnosis]
    p.outcomes = [outcome]
    p.phenotypes = [phenotype]

    # Family relationship
    inputs['/family-relationships']['participant_id'] = p1.kf_id
    inputs['/family-relationships']['relative_id'] = p2.kf_id
    fr = FamilyRelationship(**inputs['/family-relationships'])

    db.session.add(fr)

    # Add participants to study
    study.investigator = investigator
    study.study_files = [sf]
    study.participants.append(p)
    db.session.add(study)
    db.session.add(p)
    db.session.add(seq_exp)
    db.session.commit()

    # Add foreign keys
    # Study and participant
    inputs['/participants']['study_id'] = study.kf_id

    # Entity and participant
    endpoints = ['/diagnoses', '/biospecimens', '/outcomes',
                 '/phenotypes']
    for e in endpoints:
        inputs[e]['participant_id'] = p.kf_id

    inputs['/genomic-files']['biospecimen_id'] = biospecimen.kf_id
    # Study and study_files
    inputs['/study-files']['study_id'] = study.kf_id
    # Genomic File and Sequencing Experiment
    inputs['/genomic-files']['sequencing_experiment_id'] = seq_exp.kf_id
    # Sequencing_experiment and sequencing_center
    inputs['/sequencing-experiments']['sequencing_center_id'] =\
        seq_center.kf_id
    # Biospecimen and sequencing_center
    inputs['/biospecimens']['sequencing_center_id'] = seq_center.kf_id
    # Cavatica task and Cavatica app
    inputs['/cavatica-tasks']['cavatica_app_id'] = ca.kf_id
    # Cavatica task and genomic files
    inputs['/cavatica-task-genomic-files']['cavatica_task_id'] = ct.kf_id
    inputs['/cavatica-task-genomic-files']['genomic_file_id'] = gen_file.kf_id

    # Add kf_ids
    inputs['kf_ids'] = {}
    inputs['kf_ids'].update({'/studies': study.kf_id})
    inputs['kf_ids'].update({'/study-files': sf.kf_id})
    inputs['kf_ids'].update({'/investigators': investigator.kf_id})
    inputs['kf_ids'].update({'/participants': p.kf_id})
    inputs['kf_ids'].update({'/outcomes': outcome.kf_id})
    inputs['kf_ids'].update({'/phenotypes': phenotype.kf_id})
    inputs['kf_ids'].update({'/diagnoses': diagnosis.kf_id})
    inputs['kf_ids'].update({'/biospecimens': biospecimen.kf_id})
    inputs['kf_ids'].update({'/sequencing-experiments': seq_exp.kf_id})
    inputs['kf_ids'].update({'/family-relationships': fr.kf_id})
    inputs['kf_ids'].update({'/families': family.kf_id})
    inputs['kf_ids'].update({'/genomic-files': gen_file.kf_id})
    inputs['kf_ids'].update({'/cavatica-apps': ca.kf_id})
    inputs['kf_ids'].update({'/cavatica-tasks': ct.kf_id})
    inputs['kf_ids'].update({'/cavatica-task-genomic-files': ctgf.kf_id})
    inputs['kf_ids'].update({'/sequencing-centers': seq_center.kf_id})

    return inputs
