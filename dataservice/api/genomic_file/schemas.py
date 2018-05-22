from marshmallow_sqlalchemy import field_for

from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.common.schemas import (BaseSchema, IndexdFileSchema,
                                            AVAILABILITY_ENUM, COMMON_ENUM)
from dataservice.api.common.custom_fields import PatchedURLFor
from dataservice.extensions import ma
from marshmallow import post_dump
from dataservice.api.common.validation import enum_validation_generator

DATA_TYPE_ENUM = {'aligned reads': 'Aligned Reads',
                  'aligned reads index': 'Aligned Reads Index',
                  'unaligned reads': 'Unaligned Reads',
                  'simple nucleotide variation': 'Simple Nucleotide Variation',
                  'variant calls': 'Variant Calls',
                  'variant calls index': 'Variant Calls Index',
                  'gvcf': 'gVCF',
                  'gvcf index': 'gVCF Index',
                  'other': 'Other'}
DATA_TYPE_ENUM.update(COMMON_ENUM)


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

    @post_dump()
    def auto_populate_enum(self, data):
        if data['data_type'] is not None:
            data['data_type'] = DATA_TYPE_ENUM[data['data_type'].lower()]
        if data['availability'] is not None:
            data['availability'] = AVAILABILITY_ENUM[
                data['availability'].lower()]
