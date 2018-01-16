from dataservice.api.common.id_service import uuid_generator, kf_id_generator


def test_kf_id():
    """
    Test that kf_ids are generated correctly

    Generates 1000 ids and makes sure they are correct length and dont
    contain any invalid characters
    """
    for _ in range(1000):
        kf_id = kf_id_generator()
        assert len(kf_id) == 8
        assert 'I' not in kf_id
        assert 'L' not in kf_id
        assert 'O' not in kf_id
        assert 'U' not in kf_id

def test_uuid():
    """
    Test that uuids are generated correctly

    Generates 1000 ids and test for length and correct number of hyphens
    """
    for _ in range(1000):
        uuid = uuid_generator()
        assert len(uuid) == 36
        assert uuid.count('-') == 4
