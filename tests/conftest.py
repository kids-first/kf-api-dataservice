import json
import pytest

from dataservice import create_app
from dataservice.extensions import db

@pytest.yield_fixture(scope='session')
def app():
    return create_app('testing')

@pytest.yield_fixture(scope='session')
def client(app):
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield app.test_client()
    # Need to make sure we close all connections so pg won't lock tables
    db.session.close()
    db.drop_all()

@pytest.fixture
def entities(client):
    """ Creates some mock entities """
    p = {'external_id': 'test_1'}
    resp = client.post('/participants',
                       data=json.dumps(p),
                       headers={'Content-Type': 'application/json'})

    p_id = json.loads(resp.data.decode('utf-8'))['results']['kf_id']

    d = {'race': 'white',
         'participant_id': p_id}
    resp = client.post('/demographics',
                       data=json.dumps(d),
                       headers={'Content-Type': 'application/json'})

    for i in range(3):
        d = {'diagnosis': 'diagnosis_',
             'participant_id': p_id}
        resp = client.post('/diagnoses',
                           data=json.dumps(d),
                           headers={'Content-Type': 'application/json'})

@pytest.yield_fixture(scope='session')
def swagger(client):
    yield json.loads(client.get('/swagger').data.decode('utf-8'))
