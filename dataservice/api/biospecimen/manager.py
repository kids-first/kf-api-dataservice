"""
Module to help manage the create/update lifecycle of Samples and Containers

The main method in this module is the `manage_sample_containers` which is
responsible for create/updating Samples and Containers every time a Biospecimen
is created or updated. It gets called in
dataservice.api.biospecimen.resources.py

Background:
    The current Biospecimen table does not adequately model the hierarchical
    relationship between specimen groups and specimens. The Sample and
    Container tables have been created to fill in this gap.

    A Sample is a biologically equivalent group of specimens. A Sample has
    one or more Containers and a Container essentially mirrors the Biospecimen.

    The Sample and Container tables were created in order to minimize any
    changes to the existing Biospecimen table.
"""

from marshmallow import ValidationError
from flask import abort
from dataservice.extensions import db
from dataservice.api.sample.models import Sample
from dataservice.api.container.models import Container
from dataservice.api.sample.schemas import (
    SampleSchema,
)
from dataservice.api.container.schemas import (
    ContainerSchema,
)


def _create_sample_event_key(biospecimen):
    """
    Create a sample event identifier from specific fields on the Biospecimen

    Use:
        participant_id
        external_sample_id
        age_at_event_days

    Key format: <participant_id>-<external_sample_id>-<age_at_event_days>

    If age_at_event_days is null, then use the value "Not Reported"
    """
    components = [
        biospecimen.participant_id,
        biospecimen.external_sample_id,
        biospecimen.age_at_event_days
    ]

    return "-".join([str(c) if c else "Not Reported" for c in components])


def _create_concentration(biospecimen):
    """
    Create the sample concentration given the biospecimen concentration

    Only use the concentration value when the analyte_type is DNA or RNA
    """
    if biospecimen.analyte_type in ["DNA", "RNA"]:
        return biospecimen.concentration_mg_per_ml
    else:
        return None


def _get_sample_identifier(biospecimen):
    """
    Helper to extract specific Biospecimen attributes to uniquely
    identify a Sample
    """
    return {
        "sample_event_key": _create_sample_event_key(biospecimen),
        "composition": biospecimen.composition,
        "tissue_type": biospecimen.source_text_tissue_type,
        "analyte_type": biospecimen.analyte_type,
        "anatomical_location": biospecimen.source_text_anatomical_site,
        "method_of_sample_procurement":
        biospecimen.method_of_sample_procurement,
        "preservation_method": biospecimen.preservation_method,
        "concentration_mg_per_ml": _create_concentration(biospecimen)
    }


def _get_container_identifier(biospecimen):
    """
    Helper to extract specific Biospecimen attributes to uniquely identify
    a Container
    """
    return {
        "biospecimen_id": biospecimen.kf_id,
    }


def _get_visibility_params(biospecimen):
    """
    Helper method to get dict of visibility parameters from the Biospecimen
    """
    return {
        "visible": biospecimen.visible,
        "visibility_reason": biospecimen.visibility_reason,
        "visibility_comment": biospecimen.visibility_comment
    }


def _create_sample(biospecimen):
    """
    Create Sample from specific Biospecimen attributes. Validate Sample
    """
    # Extract the parameters that uniquely identify a sample
    params = _get_sample_identifier(biospecimen)
    # Add remaining sample attributes
    params.update(
        {
            "participant_id": biospecimen.participant_id,
            "external_id": biospecimen.external_sample_id,
            "volume_ul": biospecimen.volume_ul,
        }
    )
    # Set visibility params based on Biospecimen which represents both
    # sample and containers
    params.update(
        _get_visibility_params(biospecimen)
    )
    # Validate sample parameters and create sample
    try:
        sample = SampleSchema(strict=True).load(params).data
    # Params not valid
    except ValidationError as e:
        abort(400, 'could not create sample: {}'.format(e.messages))

    return sample


def _update_sample(current_sample, biospecimen):
    """
    Update Sample using specific Biospecimen attributes. Validate Sample
    """
    # Extract the parameters that uniquely identify a sample
    params = _get_sample_identifier(biospecimen)
    # Add remaining sample attributes
    params.update(
        {
            "participant_id": biospecimen.participant_id,
            "external_id": biospecimen.external_sample_id,
            "volume_ul": biospecimen.volume_ul,
        }
    )
    # Set visibility params based on Biospecimen which represents both
    # sample and containers
    params.update(
        _get_visibility_params(biospecimen)
    )
    try:
        sample = SampleSchema(strict=True).load(
            params, instance=current_sample, partial=True
        ).data
    except ValidationError as e:
        abort(400, 'could not update sample: {}'.format(e.messages))

    return sample


def _create_container(biospecimen, sample):
    """
    Create Container using specific Biospecimen attributes.
    Link Container to its associated biospecimen and sample
    Validate Container
    """
    # Extract the parameters that uniquely identify a sample
    params = _get_container_identifier(biospecimen)
    # Add remaining sample attributes
    params.update(
        {
            "biospecimen_id": biospecimen.kf_id,
            "sample_id": sample.kf_id,
            "volume_ul": biospecimen.volume_ul,
            "external_id": biospecimen.external_aliquot_id,
        }
    )
    # Set visibility params based on Biospecimen which represents both
    # sample and containers
    params.update(
        _get_visibility_params(biospecimen)
    )
    try:
        container = ContainerSchema(strict=True).load(params).data
    except ValidationError as e:
        abort(400, 'could not create container: {}'.format(e.messages))

    return container


def _update_container(current_container, biospecimen, sample):
    """
    Update Container using specific Biospecimen attributes.
    Link Container to its associated biospecimen and sample
    Validate Container
    """
    # Extract the parameters that uniquely identify a container
    params = _get_container_identifier(biospecimen)
    # Add remaining container attributes
    params.update(
        {
            "biospecimen_id": biospecimen.kf_id,
            "sample_id": sample.kf_id,
            "volume_ul": biospecimen.volume_ul,
            "external_id": biospecimen.external_aliquot_id,
        }
    )
    # Set visibility params based on Biospecimen which represents both
    # sample and containers
    params.update(
        _get_visibility_params(biospecimen)
    )
    try:
        container = ContainerSchema(strict=True).load(
            params, instance=current_container, partial=True
        ).data
    except ValidationError as e:
        abort(400, 'could not update container: {}'.format(e.messages))

    return container


def _upsert_sample(biospecimen):
    """
    Upsert Sample from specific Biospecimen attributes

    Try to find exisiting Sample first
    If it exists, update it using the Biospecimen attributes
    If it does not exist, create Sample using the Biospecimen attributes
    """
    # Extract biospecimen attributes that uniquely identify a sample
    sample_query_params = _get_sample_identifier(biospecimen)

    # Find sample if it exists
    sample = Sample.query.filter_by(**sample_query_params).first()

    # Sample does not exist, create it
    if not sample:
        sample = _create_sample(biospecimen)
    # Sample exists, update it
    else:
        sample = _update_sample(sample, biospecimen)

    db.session.add(sample)
    db.session.commit()

    return sample


def _upsert_container(biospecimen, sample):
    """
    Upsert Container from specific Biospecimen attributes and link Container
    to its associated Sample

    Try to find existing Container first
    If it exists, update it using the Biospecimen attributes
    If it does not exist, create Container using the Biospecimen attributes
    """
    # Extract biospecimen attributes that uniquely identify a container
    container_query_params = _get_container_identifier(biospecimen)

    # Find sample if it exists
    container = Container.query.filter_by(**container_query_params).first()

    # Container does not exist - create it
    if not container:
        container = _create_container(biospecimen, sample)
    # Container exists - update it
    else:
        container = _update_container(container, biospecimen, sample)

    db.session.add(container)
    db.session.commit()

    return container


def _update_sample_volume(sample_id):
    """
    Update Sample's volume with the sum of all of its container volumes
    """
    # Accumulate container volumes and update sample volume
    sample_with_containers = Sample.query.get(sample_id)
    total_volume = None
    for ct in sample_with_containers.containers:
        if ct.volume_ul is None:
            continue
        if total_volume is None:
            total_volume = ct.volume_ul
        else:
            total_volume += ct.volume_ul

    sample_with_containers.volume_ul = total_volume

    db.session.add(sample_with_containers)
    db.session.commit()

    return sample_with_containers


def manage_sample_containers(biospecimen):
    """
    Upsert a Sample and Container from the input Biospecimen
    Update the sample's volume with the sum of the container volumes
    """
    sample = _upsert_sample(biospecimen)
    _upsert_container(biospecimen, sample)
    sample = _update_sample_volume(sample.kf_id)

    return sample
