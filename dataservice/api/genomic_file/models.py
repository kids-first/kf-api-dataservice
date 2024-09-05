from dataservice.extensions import db
from dataservice.api.common.model import Base, IndexdFile, KfId
from dataservice.api.task.models import (
    TaskGenomicFile
)
from dataservice.api.biospecimen_genomic_file.models import (
    BiospecimenGenomicFile
)
from dataservice.api.read_group.models import ReadGroupGenomicFile
from dataservice.api.sequencing_experiment.models import (
    SequencingExperimentGenomicFile
)


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
    :param workflow_type: Specifies the specific tool within the workflow used
    to generate the file. For source files, this field should be NULL
    :param workflow_tool: Specifies the specific tool within the workflow used
    to generate the file. For source files, this field should be NULL
    :param workflow_version:  Indicates the major version of the workflow. For
    source files, this field should be NULL
    :param file_version_descriptor: Indicates the release status
    :param data_category: Type of data
    :param cavatica_file_id: Indicates the file ID in CAVATICA
    :param cavatica_volume: Indicates the CAVATICA volume ID, mediating cloud
    storage access
    :param workflow_endpoint: The endpoint name of the task outputs from
    CAVATICA task or the CAVATICA app output name
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
    workflow_type = db.Column(
        db.Text(),
        doc='Denotes the generic name for the workflow utilized in analysis.'
        ' For source files, this field should be NULL'
    )
    workflow_tool = db.Column(
        db.Text(),
        doc='Specifies the specific tool within the workflow used to generate'
        ' the file. For source files, this field should be NULL'
    )
    workflow_version = db.Column(
        db.Text(),
        doc='Indicates the major version of the workflow. For source files, '
        ' this field should be NULL'
    )
    file_version_descriptor = db.Column(
        db.Text(),
        doc='Inidicates release status'
    )
    data_category = db.Column(
        db.Text(),
        doc='Inidicates type of data file'
    )
    cavatica_file_id = db.Column(
        db.Text(),
        doc='Indicates the file ID in CAVATICA'
    )
    cavatica_volume = db.Column(
        db.Text(),
        doc='Indicates the CAVATICA volume ID, mediating cloud storage access'
    )
    workflow_endpoint = db.Column(
        db.Text(),
        doc='The endpoint name of the task outputs from CAVATICA task or the'
        ' CAVATICA app output name'
    )

    task_genomic_files = db.relationship(TaskGenomicFile,
                                         backref='genomic_file',
                                         cascade='all, delete-orphan')
    read_group_genomic_files = db.relationship(ReadGroupGenomicFile,
                                               backref='genomic_file',
                                               cascade='all, delete-orphan')
    sequencing_experiment_genomic_files = db.relationship(
        SequencingExperimentGenomicFile,
        backref='genomic_file',
        cascade='all, delete-orphan')
    biospecimen_genomic_files = db.relationship(BiospecimenGenomicFile,
                                                backref='genomic_file',
                                                cascade='all, delete-orphan')
