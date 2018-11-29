from sqlalchemy.ext.hybrid import hybrid_property

from dataservice.extensions import db
from dataservice.api.common.model import Base, IndexdFile, KfId
from dataservice.api.task.models import (
    TaskGenomicFile
)
from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile
)
from dataservice.api.read_group.models import ReadGroupGenomicFile


class GenomicFile(db.Model, Base, IndexdFile):
    """
    GenomicFile entity.

    A GenomicFile has fields that are stored in both the datamodel, and in
    the Gen3 indexd service. The two are linked through a common uuid.


    :param kf_id: Unique id given by the Kid's First DCC
    :param uuid: The baseid assigned to the file by indexd
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to genomic_file by contributor
    :param file_name: Name of file
    :param data_type: Type of genomic file (i.e. aligned reads)
    :param file_format: Format of file
    :param controlled_access: Whether or not the file is controlled access
    :param is_harmonized: Whether or not the file is harmonized
    :param reference_genome: Original reference genome of the
           unharmonized genomic files
    :param latest_did: UUID for the latest version of the file in indexd
    :param urls: Locations of file
    :param hashes: A dict keyed by hash type containing hashes of the file
    :param _metadata: A dict with any additional information
    :param controlled_access: whether or not the file is controlled access
    :param availability: Indicates whether a file is available for immediate
           download, or is in cold storage
    :param experiment_strategies: List of experiment_strategies on this
        file's sequencing experiments
    :param platforms: List of platforms in this file's sequencing experiments
    :param instrument_models: List of instrument_models in this file's
        sequencing experiments
    :param is_paired_end: Whether this file was generated from a paired end
        sequencing_experiment
    """
    __tablename__ = 'genomic_file'
    __prefix__ = 'GF'

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    data_type = db.Column(db.Text(), doc='Type of genomic file')
    file_format = db.Column(db.Text(), doc='Size of file in bytes')
    is_harmonized = db.Column(db.Boolean(), default=False,
                              doc='Whether or not the file is harmonized')
    reference_genome = db.Column(db.Text(), doc='Original reference genome of'
                                 ' the unharmonized genomic files')
    controlled_access = db.Column(db.Boolean(), doc='Whether or not the file'
                                  'is controlled access')
    availability = db.Column(db.Text(), doc='Indicates whether a file is '
                             'available for immediate download, or is in '
                             'cold storage')
    paired_end = db.Column(db.Integer(), doc='The direction of the read')

    sequencing_experiment_id = db.Column(KfId(),
                                         db.ForeignKey(
                                         'sequencing_experiment.kf_id'))

    task_genomic_files = db.relationship(TaskGenomicFile,
                                         backref='genomic_file',
                                         cascade='all, delete-orphan')
    read_group_genomic_files = db.relationship(ReadGroupGenomicFile,
                                               backref='genomic_file',
                                               cascade='all, delete-orphan')
    biospecimen_genomic_files = db.relationship(BiospecimenGenomicFile,
                                                backref='genomic_file',
                                                cascade='all, delete-orphan')

    @hybrid_property
    def experiment_strategies(self):
        if self.sequencing_experiment:
            v = self.sequencing_experiment.experiment_strategy
            return [] if v is None else [v]
        else:
            return []

    @experiment_strategies.expression
    def experiment_strategies(cls):
        from dataservice.api.sequencing_experiment.models import (
            SequencingExperiment
        )
        v = SequencingExperiment.experiment_strategy
        return [] if v is None else [v]

    @hybrid_property
    def platforms(self):
        if self.sequencing_experiment:
            return [self.sequencing_experiment.platform]
        else:
            return []

    @platforms.expression
    def platforms(cls):
        from dataservice.api.sequencing_experiment.models import (
            SequencingExperiment
        )
        v = SequencingExperiment.platform
        return [] if v is None else [v]

    @hybrid_property
    def instrument_models(self):
        if self.sequencing_experiment:
            v = self.sequencing_experiment.instrument_model
            return [] if v is None else [v]
        else:
            return []

    @instrument_models.expression
    def instrument_models(cls):
        from dataservice.api.sequencing_experiment.models import (
            SequencingExperiment
        )
        v = SequencingExperiment.instrument_model
        return [] if v is None else [v]

    @hybrid_property
    def is_paired_end(self):
        if self.sequencing_experiment:
            return self.sequencing_experiment.is_paired_end
        else:
            return None

    @instrument_models.expression
    def instrument_models(cls):
        from dataservice.api.sequencing_experiment.models import (
            SequencingExperiment
        )
        return SequencingExperiment.is_paired_end
