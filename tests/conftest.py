import pytest

from dataservice import create_app
from dataservice.extensions import db


@pytest.fixture
def client():
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield app.test_client()
    db.drop_all()
