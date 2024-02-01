from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.container.models import Container
from sqlalchemy import event

# Columns for Sample unique constraint
unique_cols = (
    "external_id",
    "participant_id",
    "age_at_event_days",
    "composition",
    "tissue_type",
    "analyte_type",
    "anatomical_location",
    "method_of_sample_procurement",
    "preservation_method",
    "concentration_mg_per_ml",
)
# Mapping to Biospecimen columns
col_mapping = {
    "external_id": "external_sample_id",
    "participant_id": "participant_id",
    "age_at_event_days": "age_at_event_days",
    "composition": "composition",
    "tissue_type": "source_text_tissue_type",
    "analyte_type": "analyte_type",
    "anatomical_location": "source_text_anatomical_site",
    "method_of_sample_procurement": "method_of_sample_procurement",
    "preservation_method": "preservation_method",
    "concentration_mg_per_ml": "concentration_mg_per_ml",
    "volume_ul": "volume_ul",
}


class Sample(db.Model, Base):
    """
    Sample - a biologically equivalent group of specimens

    Background:

    The current Biospecimen table does not adequately model the hierarchical
    relationship between specimen groups and specimens. The Sample and
    Container tables have been created to fill in this gap.

    A Sample is a biologically equivalent group of specimens. A Container
    represents one of the specimens in the Sample's group of specimens.

    The Sample and Container tables were created in order to minimize any
    changes to the existing Biospecimen table.

    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sample by contributor
    :param age_at_event_days: Age at the time of event occurred in number of
    days since birth
    :param sample_event_key: An identifier that represents when the sample
    was drawn
    :param composition : The cellular composition of the sample.
    :param tissue_type: description of the kind of tissue collected
           with respect to disease status or proximity to tumor tissue
    :param anatomical_location : The name of the primary disease site
           of the submitted tumor sample
    :param analyte_type: Text term that represents the kind of molecular
           specimen analyte
    :param concentration_mg_per_ml: The concentration of an analyte or aliquot
           extracted from the sample or sample portion, measured in
           milligrams per milliliter
    :param volume_ul: The volume in microliters (ul) of the aliquots derived
           from the analyte(s) shipped for sequencing and characterization
    :param preservation_method: Text term that represents the method used
           to preserve the sample
    :param method_of_sample_procurement: Text term that represents the method
           used to extract the analytes from the sample
    """

    __tablename__ = 'sample'
    __prefix__ = 'SA'
    __unique_constraint__ = db.UniqueConstraint(
        *unique_cols,
        name="sample_unique_constraint"
    )
    __table_args__ = (__unique_constraint__,)

    external_id = db.Column(
        db.Text(),
        doc='Name or ID given to sample by contributor'
    )
    age_at_event_days = db.Column(db.Integer(),
                                  doc='Age at the time of event occurred in '
                                      'number of days since birth.')
    sample_event_key = db.Column(
        db.Text(),
        doc='Identifier for event when sample was first drawn'
    )
    tissue_type = db.Column(
        db.Text(),
        doc='Description of the kind of sample collected'
    )
    composition = db.Column(
        db.Text(),
        doc='The cellular composition of the sample'
    )
    anatomical_location = db.Column(
        db.Text(),
        doc='The anatomical location of collection'
    )
    analyte_type = db.Column(
        db.Text(),
        doc='The molecular description of the sample'
    )
    concentration_mg_per_ml = db.Column(
        db.Float(),
        doc='The concentration of the sample'
    )
    volume_ul = db.Column(
        db.Float(),
        doc='The volume of the sample'
    )
    method_of_sample_procurement = db.Column(
        db.Text(),
        doc='The method used to procure the sample used to extract '
        'analyte(s)'
    )
    preservation_method = db.Column(
        db.Text(),
        doc='Text term that represents the method used to preserve the sample'
    )
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False,
                               doc='The kf_id of the sample\'s donor')
    containers = db.relationship(Container,
                                 cascade='all, delete-orphan',
                                 backref=db.backref('sample',
                                                    lazy=True))


@event.listens_for(Container, 'after_delete')
@event.listens_for(Container, 'after_update')
def delete_orphans(mapper, connection, state):
    """
    Delete samples with 0 child containers
    """
    q = (db.session.query(Sample)
         .filter(~Sample.containers.any()))
    q.delete(synchronize_session='fetch')
