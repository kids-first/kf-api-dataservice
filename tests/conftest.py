import json
from datetime import datetime
import pytest

from dataservice import create_app
from dataservice.extensions import db
from dataservice.api.investigator.models import Investigator
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.family.models import Family
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.sample.models import Sample
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.study_file.models import StudyFile


@pytest.yield_fixture(scope='session')
def app():
    yield create_app('testing')


@pytest.yield_fixture(scope='module')
def client(app):
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield app.test_client()
    # Need to make sure we close all connections so pg won't lock tables
    db.session.close()
    db.drop_all()


@pytest.yield_fixture(scope='module')
def swagger(client):
    yield json.loads(client.get('/swagger').data.decode('utf-8'))


@pytest.fixture
def entities(client):
    """
    Create mock entities
    """
    inputs = {
        '/investigators': {
            'name': 'submitter'
        },
        '/studies': {
            'external_id': 'phs001'
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
        '/samples': {
            'external_id': 's0',
            'tissue_type': 'tissue',
            'composition': 'comp',
            'anatomical_site': 'site',
            'age_at_event_days': 365,
            'tumor_descriptor': 'tumor'
        },
        '/aliquots': {
            'external_id': 'AL1',
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Baylor',
            'analyte_type': 'DNA',
            'concentration': 200,
            'volume': 13.99,
            'shipment_date': str(datetime.utcnow())
        },
        '/sequencing-experiments': {
            'external_id': 'se1',
            'experiment_date': str(datetime.utcnow()),
            'experiment_strategy': 'WGS',
            'center': 'Baylor',
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
            'diagnosis': 'diag',
            'age_at_event_days': 365
        },
        '/outcomes': {
            'vital_status': 'Alive',
            'disease_related': 'False',
            'age_at_event_days': 120,
        },
        '/phenotypes': {
            'phenotype': 'test phenotype 1',
            'hpo_id': 'HP:0000118',
            'age_at_event_days': 120
        },

        '/family-relationships': {
            'participant_to_relative_relation': 'mother'
        },
        '/study-files':{
            'file_name': 'test_file_name 1'
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
    sample = Sample(**inputs['/samples'], participant_id=p.kf_id)
    diagnosis = Diagnosis(**inputs['/diagnoses'], participant_id=p.kf_id)
    aliquot = Aliquot(**inputs['/aliquots'])
    seq_exp = SequencingExperiment(**inputs['/sequencing-experiments'])

    aliquot.sequencing_experiments = [seq_exp]
    sample.aliquots = [aliquot]
    sample.aliquots = [aliquot]
    p.samples = [sample]
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

    db.session.commit()

    # Add foreign keys
    # Study and participant
    inputs['/participants']['study_id'] = study.kf_id

    # Entity and participant
    endpoints = ['/diagnoses', '/samples', '/outcomes', '/phenotypes']
    for e in endpoints:
        inputs[e]['participant_id'] = p.kf_id

    # Sample and aliquot
    inputs['/aliquots']['sample_id'] = sample.kf_id
    # Aliquot and sequencing_experiment
    inputs['/sequencing-experiments']['aliquot_id'] = aliquot.kf_id
    # Study and study_files
    inputs['/study-files']['study_id'] = study.kf_id

    # Add kf_ids
    inputs['kf_ids'] = {}
    inputs['kf_ids'].update({'/studies': study.kf_id})
    inputs['kf_ids'].update({'/study-files': sf.kf_id})
    inputs['kf_ids'].update({'/investigators': investigator.kf_id})
    inputs['kf_ids'].update({'/participants': p.kf_id})
    inputs['kf_ids'].update({'/outcomes': outcome.kf_id})
    inputs['kf_ids'].update({'/phenotypes': phenotype.kf_id})
    inputs['kf_ids'].update({'/diagnoses': diagnosis.kf_id})
    inputs['kf_ids'].update({'/samples': sample.kf_id})
    inputs['kf_ids'].update({'/aliquots': aliquot.kf_id})
    inputs['kf_ids'].update({'/sequencing-experiments': seq_exp.kf_id})
    inputs['kf_ids'].update({'/family-relationships': fr.kf_id})
    inputs['kf_ids'].update({'/families': family.kf_id})

    return inputs
