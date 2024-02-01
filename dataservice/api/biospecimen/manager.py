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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import or_, and_

from dataservice.extensions import db
from dataservice.api.sample.models import Sample, unique_cols, col_mapping
from dataservice.api.container.models import Container
from dataservice.api.common.id_service import kf_id_generator

from pprint import pprint

create_sample_id = kf_id_generator(Sample.__prefix__)


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

def _get_visibility_params(biospecimen):
    """
    Helper method to get dict of visibility parameters from the Biospecimen
    """
    return {
        "visible": biospecimen.visible,
        "visibility_reason": biospecimen.visibility_reason,
        "visibility_comment": biospecimen.visibility_comment
    }



def _replace_nulls(payload):
    """
    NULL values in postgresql are considered distinct so when used in an 
    insert do update on conflict, this will generate duplicate rows. 

    Newer versions of postgresql (which Dataservice does not use)
    have a way to handle this but the workaround is to replace NULL
    with a common string or int or float (e.g. Not Reported) to represent NULL

    See https://dba.stackexchange.com/questions/151431/postgresql-upsert-issue-with-null-values # noqa

    This method provides a work around by replacing NULL values with some kind 
    of common nullish value
    """
    for k, v in payload.items():
        if v is None:
            if k in {"age_at_event_days", "concentration_mg_per_ml"}:
                payload[k] = -9999
            else:
                payload[k] = "Not Reported"
        else:
            continue
    return payload



def _upsert_sample(biospecimen):
    """
    Update or insert sample based on sample unique constraint
    """
    # Params from unique cols
    payload = {
        col: getattr(biospecimen, col_mapping.get(col))
        for col in unique_cols
    }
    # Rest of params
    payload.update({
        "sample_event_key": _create_sample_event_key(biospecimen),
        "volume_ul": biospecimen.volume_ul,
    })
    payload.update(_get_visibility_params(biospecimen))

    # Replace NULLS
    # See method docstring
    payload = _replace_nulls(payload)

    create_payload = payload.copy()
    create_payload["kf_id"] = create_sample_id()

    # Insert with do update on conflict
    statement = (
        insert(Sample).values(**create_payload).on_conflict_do_update(
            constraint=Sample.__unique_constraint__.name,
            set_=payload
        )
    )
    db.session.execute(statement)
    db.session.commit()


def _upsert_sample_preserve_nulls(biospecimen):
    """
    Try creating the sample. If it exists update it

    NOTE: This does not work with async / concurrent HTTP requests. It is 
    not fast enough and causes inconsistent data.

    Issues happen when create sample does not finish before next transaction.
    We would have to employ db locks to make this work. This isn't worth it.

    Better to use _upsert_sample. Has a downside of replacing NULL values
    with a nullish string/int/float. But upside is that it is consistent with 
    synchronous and async requests since it executes only 1 db transaction
    which locks the table during the transaction
    """
    unique_params = {
        col: getattr(biospecimen, col_mapping.get(col))
        for col in unique_cols
    }
    payload = unique_params
    payload.update(
        {
            "sample_event_key": _create_sample_event_key(biospecimen),
            "volume_ul": biospecimen.volume_ul,
        }
    )
    payload.update(_get_visibility_params(biospecimen))

    # Construct the query to find if the Sample exists. Here we must use
    # the filter instead of filter_by method bc filter_by only does a simple
    # search that ANDs a bunch of col == value conditions together. This
    # method doesn't work when there is a null value since col == NULL is
    # not valid SQL. For NULL values you have to use col IS NULL in the SQL.
    # In newer versions of SQLAlchemy the filter_by(**kwargs) takes care of
    # NULL values internally

    # For each col in the Sample unique constraint, construct a condition that
    # accomplishes this:
    #     (( sample.age_at_event_days == biospecimen.age_at_event_days ) or
    #     ( sample.age_at_event_days is NULL ))
    # See https://stackoverflow.com/questions/5602918/select-null-values-in-sqlalchemy/44679356#44679356
    filters = []
    for k, v in unique_params.items():
        col = getattr(Sample.__table__.c, k)
        filters.append(or_(col == v, col.is_(None)))

    updated_rows = Sample.query.filter(*filters).update(payload)
    if updated_rows == 0:
        sample = Sample(**payload)
        db.session.add(sample)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            pass


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
    # _upsert_container(biospecimen, sample)
    # sample = _update_sample_volume(sample.kf_id)

    return sample
