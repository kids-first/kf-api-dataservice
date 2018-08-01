from sqlalchemy.orm import validates
from sqlalchemy import event

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.biospecimen_diagnosis.models import (
    BiospecimenDiagnosis)


class Diagnosis(db.Model, Base):
    """
    Diagnosis entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to diagnosis by contributor
    :param source_text_diagnosis: Diagnosis of the participant
    :param diagnosis_category: High level diagnosis categorization
    :param source_text_tumor_location: Location of the tumor
    :param age_at_event_days: Age at the time of diagnosis expressed
           in number of days since birth
    :param mondo_id_diagnosis: The ID of the term from the Monary Disease
           Ontology which represents a harmonized diagnosis
    :param icd_id_diagnosis: The ID of the term from the International
           Classification of Diseases which represents a harmonized diagnosis
    :param uberon_id_tumor_location: The ID of the term from Uber-anatomy
           ontology which represents harmonized anatomical ontologies
    :param ncit_id_diagnosis: The ID term from the National Cancer Institute
           Thesaurus which represents a harmonized diagnosis
    :param spatial_descriptor: Ontology term that harmonizes the spatial
           concepts from Biological Spatial Ontology
    """
    __tablename__ = 'diagnosis'
    __prefix__ = 'DG'

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    source_text_diagnosis = db.Column(db.Text(),
                                      doc='the pathological diagnosis')
    diagnosis_category = db.Column(db.Text(),
                                   doc='High level diagnosis categorization'
                                   )
    source_text_tumor_location = db.Column(db.Text(),
                                           doc='location of the tumor')
    age_at_event_days = db.Column(db.Integer(),
                                  doc='Age at the time of event occurred in '
                                      'number of days since birth')
    mondo_id_diagnosis = db.Column(db.Text(),
                                   doc='The ID of the term from the Monary '
                                   'Disease Ontology which represents a'
                                   ' harmonized diagnosis')
    icd_id_diagnosis = db.Column(db.Text(),
                                 doc='The ID of the term from the'
                                 ' International Classification of Diseases'
                                 ' which represents harmonized diagnosis')
    uberon_id_tumor_location = db.Column(db.Text(),
                                         doc='The ID of the term from Uber '
                                         'anatomy ontology which represents'
                                         ' harmonized anatomical ontologies')
    ncit_id_diagnosis = db.Column(db.Text(),
                                  doc='The ID term from the National Cancer'
                                  ' Institute Thesaurus which represents a'
                                  ' harmonized diagnosis')
    spatial_descriptor = db.Column(db.Text(),
                                   doc='Ontology term that harmonizes the'
                                   'spatial concepts from Biological Spatial'
                                   ' Ontology')
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               doc='the participant who was diagnosed',
                               nullable=False)
    biospecimen_diagnoses = db.relationship(BiospecimenDiagnosis,
                                            backref='diagnosis',
                                            cascade='all, delete-orphan')
