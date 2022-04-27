from sqlalchemy.dialects.postgresql import UUID
from flask import current_app
from dataservice.extensions import db
from dataservice.api.common.id_service import uuid_generator
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


class GenomicFile(db.Model, Base):
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

    latest_did = db.Column(UUID(), default=uuid_generator)
    file_name = db.Column(db.Text(), doc='Name of the file')
    size = db.Column(db.BigInteger(), doc='The size of the file in bytes')
    urls = db.Column(db.ARRAY(db.Text), doc='List of file urls')
    acl = db.Column(db.ARRAY(db.Text), doc='List of ACLs')
    hashes = db.Column(db.JSON(), doc='File hashes')

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    data_type = db.Column(db.Text(), doc='Type of genomic file')
    file_format = db.Column(db.Text(), doc='Type of file')
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

    @property
    def access_urls(self):
        """
        Access urls should contain only links out to gen3 data endpoints
        that are used to download the files themselves.

        For urls that are already https:// urls, we will consider them as
        valid gen3 locations, for urls that are s3:// protocol, we will assume
        that they are internal files and resolve them to our gen3 service
        """
        urls = []
        for url in self.urls or []:
            if url.startswith('s3://'):
                url = (f'{current_app.config["GEN3_URL"]}'
                       f'/data/{self.latest_did}')
            urls.append(url)

        return urls
