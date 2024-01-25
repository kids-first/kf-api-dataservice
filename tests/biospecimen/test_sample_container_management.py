"""
Test that samples and containers are properly created/updated/deleted when a
biospecimen is created/updated
"""

import json
from flask import url_for

import pytest

from dataservice.api.container.models import Container
from dataservice.api.sample.models import Sample
from dataservice.api.biospecimen.models import Biospecimen

from tests.create import make_participant, make_seq_center

BIOSPECIMENS_URL = 'api.biospecimens'
BIOSPECIMENS_LIST_URL = 'api.biospecimens_list'


@pytest.fixture(scope="function")
def upsert_biospecimen(client, action="create", biospecimen_params=None):
    """
    Return a method to POST or PATCH a biospecimen
    """
    def _upsert_biospecimen(
        action="create", create_participant=True, biospecimen_params=None
    ):
        """
        Helper method to POST/PATCH a biospecimen 
        """
        sc = make_seq_center()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        kwargs = {
            "external_sample_id": "sa-01",
            "external_aliquot_id": "ct-01",
            "source_text_tissue_type": "Normal",
            "composition": "Blood",
            "source_text_anatomical_site": "Brain",
            "method_of_sample_procurement": "Surgical Resections",
            "age_at_event_days": 456,
            "source_text_tumor_descriptor": "Metastatic",
            "shipment_origin": "CORIELL",
            "analyte_type": "DNA",
            "concentration_mg_per_ml": 1.3,
            "volume_ul": 5,
            "spatial_descriptor": "left side",
            "consent_type": "GRU-IRB",
            "preservation_method": "Frozen",
            "sequencing_center_id": sc.kf_id
        }
        if biospecimen_params:
            kwargs.update(biospecimen_params)

        if create_participant:
            p = make_participant()
            kwargs["participant_id"] = p.kf_id

        if action == "create":
            # Send post request
            response = client.post(url_for(BIOSPECIMENS_LIST_URL),
                                   data=json.dumps(kwargs),
                                   headers=headers)

            # Check response status status_code
            assert response.status_code == 201
        else:
            kf_id = kwargs.pop("kf_id", None)
            response = client.patch(url_for(BIOSPECIMENS_URL,
                                            kf_id=kf_id),
                                    headers=headers,
                                    data=json.dumps(kwargs))

        # Check response content
        response = json.loads(response.data.decode('utf-8'))
        biospecimen = response['results']

        return biospecimen

    return _upsert_biospecimen


def check_sample(biospecimen):
    """
    Helper method to ensure Sample is populated with correct biospecimen 
    attributes
    """
    b = biospecimen
    s = Sample.query.filter_by(external_id=b.external_sample_id).one_or_none()

    # Check sample attributes were populated correctly
    s_params = {
        "participant_id": b.participant_id,
        "sample_event_key": (
            f"{b.participant_id}-{b.external_sample_id}-{b.age_at_event_days}"
        ),
        "external_id": b.external_sample_id,
        "analyte_type": b.analyte_type,
        "anatomical_location": b.source_text_anatomical_site,
        "composition": b.composition,
        "concentration_mg_per_ml": b.concentration_mg_per_ml,
        "method_of_sample_procurement": b.method_of_sample_procurement,
        "preservation_method": b.preservation_method,
        "tissue_type": b.source_text_tissue_type,
        "volume_ul": b.volume_ul,
    }
    for key, value in s_params.items():
        if key == "volume_ul":
            continue
        assert getattr(s, key) == value

    # Check volume
    total = 0
    for c in s.containers:
        if c.volume_ul:
            total += c.volume_ul
    assert total == s.volume_ul

    return s


def check_container(biospecimen, sample):
    """
    Helper method to ensure Sample is populated with correct biospecimen 
    attributes
    """
    b = biospecimen
    s = sample
    c = Container.query.filter_by(
        external_id=b.external_aliquot_id
    ).one_or_none()

    c_params = {
        "external_id": b.external_aliquot_id,
        "volume_ul": b.volume_ul,
        "biospecimen_id": b.kf_id,
        "sample_id": s.kf_id,
    }
    for key, value in c_params.items():
        assert getattr(c, key) == value

    return c


def test_create_new_biospecimen(upsert_biospecimen):
    """
    Create a new specimen with no existing specimens

    Should result in 1 new Sample and 1 new Container
    """
    # Create specimen and call the manage_sample_containers method to
    # derive sample and container
    b_resp = upsert_biospecimen()

    # Get Biospecimen from db
    b = Biospecimen.query.get(b_resp["kf_id"])

    # Check sample, container counts
    assert Sample.query.count() == 1
    assert Container.query.count() == 1

    # Check sample was created correctly
    s = check_sample(b)

    # Check container was created properly
    check_container(b, s)


def test_create_two_biospecimens_diff_container(client, upsert_biospecimen):
    """
    Create a new specimen. Then create another specimen with same parameters
    and a different aliquot_id than first specimen

    Should result in 1 Sample, 2 Container

    - Create first specimen bs1
      -> create sample sa-01, create container ct-01 for bs1
    - Create second specimen bs2
      -> find sa-01, create container ct-02 for bs2
         linked to sa-01 and bs2
    """
    # Create specimen and call the manage_sample_containers method to
    # derive sample and container
    Container.query.delete()
    Biospecimen.query.delete()

    b1_resp = upsert_biospecimen()
    b2_resp = upsert_biospecimen(
        biospecimen_params={"external_aliquot_id": "ct-02"}
    )

    # Check sample, container counts
    assert Sample.query.count() == 1
    assert Container.query.count() == 2

    # Get Biospecimen from db
    b1 = Biospecimen.query.get(b1_resp["kf_id"])
    b2 = Biospecimen.query.get(b2_resp["kf_id"])
    specimens = [b1, b2]

    # Check sample was created correctly
    s = check_sample(b2)
    assert len(s.containers) == 2

    # Check container was created properly
    for i, _ in enumerate(s.containers):
        check_container(specimens[i], s)


def test_create_two_biospecimens_diff_sample_and_container(
    client, upsert_biospecimen
):
    """
    Create a new specimen. Then create another specimen with same parameters
    and a different sample_id and aliquot_id than first specimen

    Should result in 2 Sample, 2 Container

    - Create first specimen bs1
      -> create sample sa-01, create container ct-01 for bs1
    - Create second specimen bs2
      -> create sample sa-02, create container ct-02 for bs2
         linked to sa-02 and bs2 
    """
    # Create specimen and call the manage_sample_containers method to
    # derive sample and container
    Container.query.delete()
    Biospecimen.query.delete()

    b1_resp = upsert_biospecimen()
    b2_resp = upsert_biospecimen(
        biospecimen_params={
            "external_sample_id": "sa-02",
            "external_aliquot_id": "ct-02"
        }
    )

    # Check sample, container counts
    assert Sample.query.count() == 2
    assert Container.query.count() == 2

    # Get Biospecimen from db
    b1 = Biospecimen.query.get(b1_resp["kf_id"])
    b2 = Biospecimen.query.get(b2_resp["kf_id"])
    specimens = [b1, b2]

    # Check sample was created correctly
    samples = []
    for b in specimens:
        s = check_sample(b)
        samples.append(s)

    # Check container was created properly
    for i, _ in enumerate(s.containers):
        check_container(specimens[i], samples[i])


def test_update_biospecimen_aliquot_id(client, upsert_biospecimen):
    """
    Create a new specimen. Update specimen with different aliquot_id

    Should result in 1 new Sample and 1 new Container

    - Create first specimen bs1
      -> create sample sa-01, create container ct-01 for bs1
    - Update specimen bs1 with external_aliquot_id = ct-02
      -> find sample sa-01, find container ct-01 and update aliquot_id 
    """
    # Create specimen and call the manage_sample_containers method to
    # derive sample and container
    Container.query.delete()
    Biospecimen.query.delete()

    b1_resp = upsert_biospecimen()
    b1_resp = upsert_biospecimen(
        action="update",
        biospecimen_params={
            "external_aliquot_id": "ct-02",
            "kf_id": b1_resp["kf_id"]
        }
    )

    # Check sample, container counts
    assert Sample.query.count() == 1
    assert Container.query.count() == 1

    # Get Biospecimen from db
    b1 = Biospecimen.query.get(b1_resp["kf_id"])

    # Check sample was created correctly
    s = check_sample(b1)

    # Check container was created properly
    check_container(b1, s)


def test_update_biospecimen_sample_id(client, upsert_biospecimen):
    """
    Create a new specimen. Update specimen with different sample_id

    Should result in 1 new Sample and 1 new Container

    - Create first specimen bs1
      -> create sample sa-01, create container ct-01 for bs1
    - Update specimen bs1 with external_sample_id = sa-02 
      -> create new sample sa-02, find container ct-01 and update sample link
    - Delete orphaned sample sa-01
    """
    # Create specimen and call the manage_sample_containers method to
    # derive sample and container
    Container.query.delete()
    Biospecimen.query.delete()

    b1_resp = upsert_biospecimen()
    b1_resp = upsert_biospecimen(
        action="update",
        biospecimen_params={
            "external_sample_id": "sa-02",
            "kf_id": b1_resp["kf_id"]
        }
    )

    # Check sample, container counts
    assert Sample.query.count() == 1
    assert Container.query.count() == 1

    # Get Biospecimen from db
    b1 = Biospecimen.query.get(b1_resp["kf_id"])

    # Check sample was created correctly
    s = check_sample(b1)

    # Check container was created properly
    check_container(b1, s)


def test_update_biospecimen_sample_and_aliquot_id(client, upsert_biospecimen):
    """
    Create a new specimen. Update specimen with different
    aliquot_id and sample_id

    Should result in 2 new Sample and 2 new Container

    - Create first specimen bs1
      -> create sample sa-01, create container ct-01 for bs1
    - Update specimen bs1 with external_sample_id = sa-02, external_aliquot_id
      = ct-02
      -> create new sample sa-02, find container ct-01 and update sample link
      and aliquot_id
    - Delete orphaned sample sa-01
    """
    # Create specimen and call the manage_sample_containers method to
    # derive sample and container
    Container.query.delete()
    Biospecimen.query.delete()

    b1_resp = upsert_biospecimen()
    b1_resp = upsert_biospecimen(
        action="update",
        biospecimen_params={
            "external_sample_id": "sa-02",
            "external_aliquot_id": "ct-02",
            "kf_id": b1_resp["kf_id"]
        }
    )

    # Check sample, container counts
    assert Sample.query.count() == 1
    assert Container.query.count() == 1

    # Get Biospecimen from db
    b1 = Biospecimen.query.get(b1_resp["kf_id"])

    # Check sample was created correctly
    s = check_sample(b1)

    # Check container was created properly
    check_container(b1, s)
