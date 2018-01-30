import pytest

from dataservice import create_app
from dataservice.extensions import db

@pytest.yield_fixture
def app():
    return create_app('testing')

@pytest.yield_fixture
def client(app):
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield app.test_client()
    # Need to make sure we close all connections so pg won't lock tables
    db.session.close()
    db.drop_all()
