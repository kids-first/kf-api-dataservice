from sqlalchemy.orm import validates

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


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
    biospecimen_id = db.Column(KfId(),
                               db.ForeignKey('biospecimen.kf_id'),
                               doc='the biospecimen which recieved the '
                               'diagnosis',
                               nullable=True)

    @validates('biospecimen_id')
    def validate_biospecimen(self, key, value):
        """
        Ensure that both the diagnosis and biospecimen
        (referred to by biospecimen_id) have the same participant

        If this is not the case then raise DatabaseValidationError
        """
        from dataservice.api.biospecimen.models import Biospecimen
        from dataservice.api.errors import DatabaseValidationError

        if ((self.kf_id is None and self.participant_id is None) or
                value is None):
            return None

        # Get biospecimen by id
        bsp = Biospecimen.query.get(value)

        # If it doesn't exist, return the original input value
        # and let ORM handle non-existent foreign key
        if bsp is None:
            return value

        # Check if this diagnosis and biospecimen refer to same participant
        if self.participant_id != bsp.participant_id:
            operation = 'modify'
            target_entity = Diagnosis.__tablename__
            kf_id = self.kf_id or ''
            message = (
                ('a diagnosis cannot be linked with a biospecimen if they '
                 'refer to different participants. diagnosis {} '
                 'refers to participant {} and '
                 'biospecimen {} refers to participant {}')
                .format(kf_id,
                        self.participant_id,
                        bsp.kf_id,
                        bsp.participant_id))
            raise DatabaseValidationError(target_entity, operation, message)

        return value
