from datetime import datetime

from dataservice.extensions import db
from dataservice.api.sample.models import Sample
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study


def make_study(external_id="phs001", force_create=False, **kwargs):
    """
    Make study
    """
    if force_create:
        s = None
    else:
        s = Study.query.filter_by(external_id=external_id).one_or_none()

    if not s:
        kwargs["external_id"] = external_id
        s = Study(**kwargs)
        db.session.add(s)
        db.session.commit()

    return s


def make_participant(external_id='p1', force_create=False, **kwargs):
    """
    Make a sample
    """
    if force_create:
        p = None
    else:
        p = Participant.query.filter_by(external_id=external_id).one_or_none()

    if not p:
        kwargs["external_id"] = external_id
        p = Participant(**kwargs)

        s = make_study()
        s.participants.extend([p])
        db.session.add(s)
        db.session.commit()

    return p


def make_biospecimen(
    external_sample_id='bs1', external_aliquot_id='bs1',
    sample=None, force_create=False, **kwargs
):
    """
    Make a biospecimen
    """
    if force_create:
        bs = None
    else:
        bs = Biospecimen.query.filter_by(
            external_sample_id=external_sample_id,
            external_aliquot_id=external_aliquot_id,
        ).one_or_none()
    if not bs:
        dt = datetime.now()
        p = make_participant()
        sc = make_seq_center()
        body = {
            'external_sample_id': external_sample_id,
            'external_aliquot_id': external_aliquot_id,
            'source_text_tissue_type': 'Normal',
            'composition': 'blood',
            'source_text_anatomical_site': 'Brain',
            'age_at_event_days': 456,
            'source_text_tumor_descriptor': 'Metastatic',
            'shipment_origin': 'CORIELL',
            'analyte_type': 'DNA',
            'concentration_mg_per_ml': 100.0,
            'volume_ul': 12.67,
            'shipment_date': dt,
            'uberon_id_anatomical_site': 'UBERON:0000955',
            'spatial_descriptor': 'left side',
            'ncit_id_tissue_type': 'Test',
            'ncit_id_anatomical_site': 'C12439',
            'consent_type': 'GRU-IRB',
            'dbgap_consent_code': 'phs00000.c1',
            'preservation_method': 'Frozen',
            "participant_id": p.kf_id,
            "sequencing_center_id": sc.kf_id
        }
        body.update(kwargs)
        bs = Biospecimen(**body)
        if not sample:
            sample = make_sample(force_create=True)
        bs.sample_id = sample.kf_id
        db.session.add(bs)
        db.session.commit()

    return bs


def make_sample(external_id='sample-01', force_create=False, **kwargs):
    """
    Make a sample
    """
    if force_create:
        s = None
    else:
        s = Sample.query.filter_by(external_id=external_id).one_or_none()

    if not s:
        p1 = make_participant()
        kwargs["external_id"] = external_id
        s = Sample(**kwargs)
        s.participant = p1
        db.session.add(s)
        db.session.commit()

    return s


def make_seq_center(name="Baylor", force_create=False, **kwargs):
    """
    Make a sequencing_center
    """
    sc = SequencingCenter.query.filter_by(name=name).one_or_none()
    if sc is None:
        kwargs["name"] = name
        sc = SequencingCenter(**kwargs)
    db.session.add(sc)
    db.session.commit()

    return sc
