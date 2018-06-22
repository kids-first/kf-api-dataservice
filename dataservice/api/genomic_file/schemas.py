from marshmallow_sqlalchemy import field_for

from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.common.schemas import (BaseSchema, IndexdFileSchema,
                                            AVAILABILITY_ENUM)
from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.extensions import ma
from dataservice.api.common.validation import enum_validation_generator

DATA_TYPE_ENUM = {'Aligned Reads',
                  'Aligned Reads Index',
                  'Unaligned Reads',
                  'Simple Nucleotide Variation',
                  'Variant Calls',
                  'Variant Calls Index',
                  'gVCF',
                  'gVCF Index',
                  'Other'}


class GenomicFileSchema(BaseSchema, IndexdFileSchema):
    class Meta(BaseSchema.Meta, IndexdFileSchema.Meta):
        model = GenomicFile
        resource_url = 'api.genomic_files'
        collection_url = 'api.genomic_files_list'

        exclude = (BaseSchema.Meta.exclude +
                   ('biospecimen', 'sequencing_experiment',) +
                   ('cavatica_task_genomic_files', 'read_group',))

    data_type = field_for(GenomicFile, 'data_type',
                          validate=enum_validation_generator(
                              DATA_TYPE_ENUM))
    availability = field_for(GenomicFile, 'availability',
                             validate=enum_validation_generator(
                                 AVAILABILITY_ENUM))

    sequencing_experiment_id = field_for(GenomicFile,
                                         'sequencing_experiment_id',
                                         load_only=True)

    biospecimen_id = field_for(GenomicFile,
                               'biospecimen_id',
                               load_only=True)

    latest_did = field_for(GenomicFile,
                           'latest_did',
                           required=False,
                           dump_only=True)

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'biospecimen': PatchedURLFor(
            'api.biospecimens',
            kf_id='<biospecimen_id>'),
        'sequencing_experiment': PatchedURLFor(
            'api.sequencing_experiments',
            kf_id='<sequencing_experiment_id>'),
        'cavatica_task_genomic_files': ma.URLFor(
            'api.cavatica_task_genomic_files_list', genomic_file_id='<kf_id>'),
        'read_group': PatchedURLFor(
            'api.read_groups', kf_id='<read_group.kf_id>')
    }, description='Resource links and pagination')
