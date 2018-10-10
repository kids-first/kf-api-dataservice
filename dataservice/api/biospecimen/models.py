from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile)
from dataservice.api.diagnosis.models import Diagnosis
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import event


class Biospecimen(db.Model, Base):
    """
    Biospecimen entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_sample_id: Name given to sample by contributor
    :param external_aliquot_id: Name given to aliquot by contributor
    :param composition : The cellular composition of the biospecimen.
    :param source_text_tissue_type: description of the kind of tissue collected
           with respect to disease status or proximity to tumor tissue
    :param source_text_anatomical_site : The name of the primary disease site
           of the submitted tumor biospecimen
    :param age_at_event_days: Age at the time biospecimen was
           acquired, expressed in number of days since birth
    :param source_text_tumor_descriptor: The kind of disease present in the
           tumor specimen as related to a specific timepoint
    :param shipment_origin : The origin of the shipment
    :param analyte_type: Text term that represents the kind of molecular
           specimen analyte
    :param concentration_mg_per_ml: The concentration of an analyte or aliquot
           extracted from the biospecimen or biospecimen portion, measured in
           milligrams per milliliter
    :param volume_ul: The volume in microliters (ul) of the aliquots derived
           from the analyte(s) shipped for sequencing and characterization
    :param shipment_date: The date item was shipped in YYYY-MM-DD format
    :param uberon_id_anatomical_site: The ID of the term from Uber-anatomy
           ontology which represents harmonized anatomical ontologies
    :param ncit_id_tissue_type: The ID term from the National Cancer Institute
           Thesaurus which represents a harmonized tissue_type
    :param ncit_id_anatomical_site: The ID term from the National Cancer
           Institute Thesaurus which represents a harmonized anatomical_site
    :param spatial_descriptor: Ontology term that harmonizes the spatial
           concepts from Biological Spatial Ontology
    :param consent_type: Short name of consent
    :param dbgap_consent_code: Consent classification code from dbgap
    """

    __tablename__ = 'biospecimen'
    __prefix__ = 'BS'

    external_sample_id = db.Column(db.Text(),
                                   doc='Name given to sample by contributor')
    external_aliquot_id = db.Column(db.Text(),
                                    doc='Name given to aliquot by contributor')
    source_text_tissue_type = db.Column(db.Text(),
                                        doc='Description of the kind of '
                                        'biospecimen collected')
    composition = db.Column(db.Text(),
                            doc='The cellular composition of the biospecimen')
    source_text_anatomical_site = db.Column(db.Text(),
                                            doc='The anatomical location of '
                                            'collection')
    age_at_event_days = db.Column(db.Integer(),
                                  doc='Age at the time of event occurred in '
                                      'number of days since birth.')
    source_text_tumor_descriptor = db.Column(db.Text(),
                                             doc='Disease present in the '
                                             'biospecimen')
    shipment_origin = db.Column(db.Text(),
                                doc='The original site of the aliquot')
    analyte_type = db.Column(db.Text(), nullable=False,
                             doc='The molecular description of the aliquot')
    concentration_mg_per_ml = db.Column(db.Float(),
                                        doc='The concentration of the aliquot')
    volume_ul = db.Column(db.Float(),
                          doc='The volume of the aliquot')
    shipment_date = db.Column(db.DateTime(),
                              doc='The date the aliquot was shipped')
    uberon_id_anatomical_site = db.Column(db.Text(),
                                          doc='The ID of the term from '
                                          'Uber-anatomy ontology which '
                                          'represents harmonized anatomical'
                                          ' ontologies')
    ncit_id_tissue_type = db.Column(db.Text(),
                                    doc='The ID term from the National Cancer'
                                    'Institute Thesaurus which represents a '
                                    'harmonized tissue_type')
    ncit_id_anatomical_site = db.Column(db.Text(),
                                        doc='The ID term from the National'
                                        'Cancer Institute Thesaurus which '
                                        'represents a harmonized'
                                        ' anatomical_site')
    spatial_descriptor = db.Column(db.Text(),
                                   doc='Ontology term that harmonizes the'
                                   'spatial concepts from Biological Spatial'
                                   ' Ontology')
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False,
                               doc='The kf_id of the biospecimen\'s donor')
    sequencing_center_id = db.Column(KfId(),
                                     db.ForeignKey('sequencing_center.kf_id'),
                                     nullable=False,
                                     doc='The kf_id of the sequencing center')
    consent_type = db.Column(db.Text(),
                             doc='Short name of consent')
    dbgap_consent_code = db.Column(db.Text(),
                                   doc='Consent classification code from dbgap'
                                   )
    genomic_files = association_proxy(
        'biospecimen_genomic_files', 'genomic_file',
        creator=lambda genomic_file:
        BiospecimenGenomicFile(genomic_file=genomic_file))

    diagnoses = association_proxy(
        'biospecimen_diagnoses', 'diagnosis',
        creator=lambda dg: BiospecimenDiagnosis(diagnosis=dg))

    biospecimen_genomic_files = db.relationship(BiospecimenGenomicFile,
                                                backref='biospecimen',
                                                cascade='all, delete-orphan')


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
    external_id = db.Column(db.Text(), doc='external id used by contributor')

    biospecimen = db.relationship(Biospecimen, backref=db.backref(
        'biospecimen_diagnoses',
        cascade='all, delete-orphan'))

    diagnosis = db.relationship(Diagnosis, backref=db.backref(
        'biospecimen_diagnoses',
        cascade='all, delete-orphan'))


def validate_diagnosis_biospecimen(target):
    """
    Ensure that both the diagnosis and biospecimen
    have the same participant
    If this is not the case then raise DatabaseValidationError
    """
    from dataservice.api.errors import DatabaseValidationError
    # Return if biospecimen_diagnosis is None
    if not target:
        return

    # Get biospecimen and diagnosis by id
    bsp = None
    ds = None
    if target.biospecimen_id and target.diagnosis_id:
        bsp = Biospecimen.query.get(target.biospecimen_id)
        ds = Diagnosis.query.get(target.diagnosis_id)

    # If biospecimen and diagnosis doesn't exist, return and
    # let ORM handle non-existent foreign key
    if bsp is None or ds is None:
        return

    # Check if this diagnosis and biospecimen refer to same participant
    if ds.participant_id != bsp.participant_id:
        operation = 'modify'
        target_entity = BiospecimenDiagnosis.__tablename__
        message = (
            ('a diagnosis cannot be linked with a biospecimen if they '
             'refer to different participants. diagnosis {} '
             'refers to participant {} and '
             'biospecimen {} refers to participant {}')
            .format(ds.kf_id,
                    ds.participant_id,
                    bsp.kf_id,
                    bsp.participant_id))
        raise DatabaseValidationError(target_entity, operation, message)


@event.listens_for(BiospecimenDiagnosis, 'before_insert')
@event.listens_for(BiospecimenDiagnosis, 'before_update')
def biospecimen_or_diagnosis_on_insert(mapper, connection, target):
    """
    Run preprocessing/validation of diagnosis before insert
    """
    validate_diagnosis_biospecimen(target)
