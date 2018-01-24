from dataservice.extensions import db
from dataservice.api.common.model import Base


diagnoses_assoc_table = db.Table('diagnoses',
                                 db.Column('diagnosis_id', db.Integer,
                                           db.ForeignKey('diagnosis.kf_id'),
                                           primary_key=True),
                                 db.Column('participant_id', db.Integer,
                                           db.ForeignKey('participant.kf_id'),
                                           primary_key=True))


class Participant(db.Model, Base):
    """
    Participant entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to participant by contributor
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = "participant"
    external_id = db.Column(db.String(32))
    diagnoses = db.relationship('Diagnosis', secondary=diagnoses_assoc_table,
                                lazy='joined',
                                backref=db.backref('participants',
                                                   lazy=True))
