from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile)
from sqlalchemy.ext.associationproxy import association_proxy


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
    :param volume_ml: The volume in microliters (ml) of the aliquots derived
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
    volume_ml = db.Column(db.Float(),
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
    dbgap_consent_code = db.Column(db.Text(),
                                   doc='Consent classification code from dbgap'
                                   )
    genomic_files = db.relationship(GenomicFile,
                                    cascade="all, delete-orphan",
                                    backref=db.backref(
                                        'biospecimen', lazy=True),
                                    doc='genomic files this biospecimen')
    diagnoses = db.relationship(Diagnosis,
                                backref=db.backref('biospecimen',
                                                   lazy=True))
    # Adding mtom_ prefix to differentiate association table attributes
    mtom_genomic_files = association_proxy(
        'biospecimen_genomic_files', 'genomic_file',
        creator=lambda genomic_file:
        BiospecimenGenomicFile(genomic_file=genomic_file))
    biospecimen_genomic_files = db.relationship(BiospecimenGenomicFile,
                                                backref='biospecimen',
                                                cascade='all, delete-orphan')
