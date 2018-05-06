import pytest
import random
import re
import string
from dataservice.api.common.model import Base
from dataservice.api.common.id_service import uuid_generator, kf_id_generator


def test_kf_id():
    """
    Test that kf_ids are generated correctly

    Generates 1000 ids and makes sure they are correct length and dont
    contain any invalid characters
    """

    for _ in range(1000):
        prefix = ''.join(random.sample(string.ascii_uppercase, 2))
        kf_id = kf_id_generator(prefix)()
        assert kf_id[:2] == prefix
        assert len(kf_id) == 11
        assert kf_id[2] == '_'

        assert 'I' not in kf_id[2:]
        assert 'L' not in kf_id[2:]
        assert 'O' not in kf_id[2:]
        assert 'U' not in kf_id[2:]

        assert re.search(r'^'+prefix+r'_[A-HJ-KM-NP-TV-Z0-9]{8}', kf_id)

def test_kf_id_field(client):
    from dataservice.extensions import db

    class TestModel(Base, db.Model):
        __prefix__ = 'TT'
        field = db.Column(db.String)

    db.create_all()
    with db.session.no_autoflush as s:
        t = TestModel(field='test')
        s.add(t)
        s.flush()
        assert t.kf_id[:3] == 'TT_'
        s.rollback()


@pytest.mark.parametrize('cls', Base.__subclasses__())
def test_has_prefix(cls):
    """
    Check that all models that derive base have defined a prefix
    """
    assert hasattr(cls, '__prefix__')
    assert type(cls.__prefix__) is str
    assert len(cls.__prefix__) == 2
    assert cls.__prefix__ != '__', '{} does not have a prefix'.format(cls)


@pytest.mark.parametrize('cls', Base.__subclasses__())
def test_has_unique_prefix(cls):
    """
    Check that no models have the same prefix
    """
    for cls2 in Base.__subclasses__():
        if cls2 != cls and cls.__prefix__ == cls2.__prefix__:
            raise AssertionError(
                '{} and {} both use {}'.format(cls, cls2, cls.__prefix__))


def test_uuid():
    """
    Test that uuids are generated correctly

    Generates 1000 ids and test for length and correct number of hyphens
    """
    for _ in range(1000):
        uuid = uuid_generator()
        assert len(uuid) == 36
        assert uuid.count('-') == 4
