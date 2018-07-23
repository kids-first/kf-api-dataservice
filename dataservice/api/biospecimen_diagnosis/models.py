from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from sqlalchemy import event
from sqlalchemy.orm import validates


class BiospecimenDiagnosis(db.Model, Base):
    """
    Represents association table between biospecimen table and
    diagnosis table. Contains all biospecimen, diagnosis combiniations.
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """

    __tablename__ = 'biospecimen_diagnosis'
    __prefix__ = 'BD'
    __table_args__ = (db.UniqueConstraint('diagnosis_id',
                                          'biospecimen_id'),)
    diagnosis_id = db.Column(KfId(),
                             db.ForeignKey('diagnosis.kf_id'),
                             nullable=False)

    biospecimen_id = db.Column(KfId(),
                               db.ForeignKey('biospecimen.kf_id'),
                               nullable=False)


def validate_diagnosis_biospecimen(target):
    """
    Ensure that both the diagnosis and biospecimen
    (referred to by biospecimen_id) have the same participant

    If this is not the case then raise DatabaseValidationError
    """
    from dataservice.api.biospecimen_diagnosis.models import (
        BiospecimenDiagnosis)
    from dataservice.api.errors import DatabaseValidationError

    # Return if diagnosis is None
    if not target:
        return

    # Get biospecimen by id
    bsp = None
    if target.biospecimen_id:
        bsp = BiospecimenDiagnosis.query.get(target.biospecimen_id)

    # If biospecimen doesn't exist, return and
    # let ORM handle non-existent foreign key
    if bsp is None:
        return

    # Check if this diagnosis and biospecimen refer to same participant
    if target.participant_id != bsp.participant_id:
        operation = 'modify'
        target_entity = BiospecimenDiagnosis.__tablename__
        kf_id = target.kf_id or ''
        message = (
            ('a diagnosis cannot be linked with a biospecimen if they '
             'refer to different participants. diagnosis {} '
             'refers to participant {} and '
             'biospecimen {} refers to participant {}')
            .format(kf_id,
                    target.participant_id,
                    bsp.kf_id,
                    bsp.participant_id))
        raise DatabaseValidationError(target_entity, operation, message)


@event.listens_for(BiospecimenDiagnosis, 'before_insert')
def diagnosis_on_insert(mapper, connection, target):
    """
    Run preprocessing/validation of diagnosis before insert
    """
    validate_diagnosis_biospecimen(target)


@event.listens_for(BiospecimenDiagnosis, 'before_update')
def diagnosis_on_update(mapper, connection, target):
    """
    Run preprocessing/validation of diagnosis before update
    """
    validate_diagnosis_biospecimen(target)
