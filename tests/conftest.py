import json
from datetime import datetime
from dateutil import tz
import pytest

from dataservice import create_app
from dataservice.extensions import db
from dataservice.api.investigator.models import Investigator
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.demographic.models import Demographic
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.sample.models import Sample
from dataservice.api.aliquot.models import Aliquot


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
            'external_id': 'AL1',
            'shipment_origin': 'CORIELL',
            'shipment_destination': 'Baylor',
            'analyte_type': 'DNA',
            'concentration': 200,
            'volume': 13.99,
            'shipment_date': str(datetime.utcnow())
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
    investigator = Investigator(**inputs['/investigators'])
    study = Study(**inputs['/studies'])
    p = Participant(**inputs['/participants'])
    demo = Demographic(**inputs['/demographics'])
    sample = Sample(**inputs['/samples'])
    aliquot = Aliquot(**inputs['/aliquots'])
    diagnosis = Diagnosis(**inputs['/diagnoses'])

    sample.aliquots = [aliquot]
    p.demographic = demo
    p.samples = [sample]
    p.diagnoses = [diagnosis]

    # Add participants to study
    study.investigator = investigator
    study.participants.append(p)

    db.session.add(study)
    db.session.commit()

    # Add foreign keys
    # Study and participant
    inputs['/participants']['study_id'] = study.kf_id

    # Entity and participant
    endpoints = ['/demographics', '/diagnoses', '/samples', '/outcomes',
                 '/phenotypes']
    for e in endpoints:
        inputs[e]['participant_id'] = p.kf_id

    # Sample and aliquot
    inputs['/aliquots']['sample_id'] = sample.kf_id

    # Add kf_ids
    inputs['kf_ids'] = {}
    inputs['kf_ids'].update({'/studies': study.kf_id})
    inputs['kf_ids'].update({'/investigators': investigator.kf_id})
    inputs['kf_ids'].update({'/participants': p.kf_id})
    inputs['kf_ids'].update({'/demographics': p.demographic.kf_id})
    inputs['kf_ids'].update({'/diagnoses': diagnosis.kf_id})
    inputs['kf_ids'].update({'/samples': sample.kf_id})
    inputs['kf_ids'].update({'/aliquots': aliquot.kf_id})

    return inputs
