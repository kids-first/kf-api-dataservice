import datetime
import uuid
import random
import pytest

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.biospecimen.models import BiospecimenGenomicFile
from dataservice.api.task.models import Task, TaskGenomicFile

from tests.utils import IndexdTestCase
from tests.mocks import MockIndexd, MockResp


MAX_SIZE_MB = 5000
MIN_SIZE_MB = 1000
MB_TO_BYTES = 1000000000


class ModelTest(IndexdTestCase):
    """
    Test GenomicFile database model
    """

    def test_create_and_find(self):
        """
        Test create genomic file
        """
        # Create genomic file dependent entities
        self._create_save_dependents()

        self.assertEqual(Participant.query.count(), 1)
        self.assertEqual(Biospecimen.query.count(), 2)

        se = SequencingExperiment.query.all()[0]

        # Properties keyed on kf_id
        kwargs_dict = {}
        for i in range(2):
            kwargs = {
                'external_id': 'genomic_file_{}'.format(i),
                'file_name': 'file_{}'.format(i),
                'data_type': 'submitted aligned reads',
                'file_format': '.cram',
                'urls': ['s3://file_{}'.format(i)],
                'hashes': {'md5': str(uuid.uuid4())},
                'controlled_access': True,
                'is_harmonized': True,
                'reference_genome': 'Test01',
                'paired_end': 1,
                'availability': 'Immediate Download',
                'sequencing_experiment_id': se.kf_id
            }
            # Add genomic file to db session
            gf = GenomicFile(**kwargs)
            db.session.add(gf)
            db.session.flush()
            kwargs['kf_id'] = gf.kf_id
            kwargs_dict[kwargs['kf_id']] = kwargs
        db.session.commit()

        # Check all input field values with persisted field values
        # for each genomic file
        self.indexd.Session().get.side_effect = None
        for kf_id, kwargs in kwargs_dict.items():
            # Mock out the response from indexd for the file
            mock_file = {
                'file_name': kwargs['file_name'],
                'urls': kwargs['urls'],
                'hashes': kwargs['hashes']
            }
            self.indexd.Session().get.return_value = MockResp(resp=mock_file)

            gf = GenomicFile.query.get(kf_id)
            gf.merge_indexd()
            for k, v in kwargs.items():
                self.assertEqual(getattr(gf, k), v)

    def test_update(self):
        """
        Test update genomic file
        """
        # Create and save genomic files and dependent entities
        kwargs_dict = self._create_save_genomic_files()

        # Update fields
        kwargs = kwargs_dict[list(kwargs_dict.keys())[0]]
        kwargs['file_name'] = 'updated file name'
        kwargs['data_type'] = 'Simple Nucleotide Variation'
        gf = GenomicFile.query.get(kwargs['kf_id'])
        [setattr(gf, k, v)
         for k, v in kwargs.items()]
        db.session.commit()

        # Check database
        gf = GenomicFile.query.get(kwargs['kf_id'])
        [self.assertEqual(getattr(gf, k), v)
         for k, v in kwargs.items()]

    def test_update_indexd_only(self):
        """
        Test updating of only indexd fields
        """
        # Create and save genomic files and dependent entities
        kwargs_dict = self._create_save_genomic_files()

        kwargs = kwargs_dict[list(kwargs_dict.keys())[1]]

        # Update fields
        gf = GenomicFile.query.get(kwargs['kf_id'])
        gf.external_id = 'blah'
        gf.size = 1234
        gf.acl = ['new_acl']
        gf._metadata = {'test': 'test'}
        did = gf.latest_did
        db.session.commit()

        # Check database
        gf = GenomicFile.query.get(kwargs['kf_id'])
        assert gf.size == 1234

        assert self.indexd.Session().post.call_count == 3

        expected = MockIndexd.doc_base.copy()
        expected.update({
            'size': 1234,
            'acl': ["new_acl"],
            'metadata': {'test': 'test'},
        })
        self.indexd.Session().post.assert_any_call(
            '{}?rev={}'.format(did, gf.rev), json=expected)

    def test_update_acl_only(self):
        """
        Test updating of only acl field
        """
        # Create and save genomic files and dependent entities
        kwargs_dict = self._create_save_genomic_files()

        kwargs = kwargs_dict[list(kwargs_dict.keys())[1]]

        # Update fields
        gf = GenomicFile.query.get(kwargs['kf_id'])
        gf.acl = ['INTERNAL', 'new_acl']
        did = gf.latest_did
        # explicitly tell the object to update one of the mapped fields
        gf.modified_at = datetime.datetime.now()
        db.session.commit()

        # Check database
        gf = GenomicFile.query.get(kwargs['kf_id'])
        assert gf.acl == ['INTERNAL', 'new_acl']

        # Update document and all versions
        assert self.indexd.Session().put.call_count == 4

        expected = {
            'file_name': 'hg38.bam',
            'acl': ['INTERNAL', 'new_acl'],
            'urls': ['s3://bucket/key'],
            'metadata': {}
        }
        self.indexd.Session().put.assert_any_call(
            '{}?rev={}'.format(did, gf.rev), json=expected)

    def test_delete(self):
        """
        Test delete existing genomic file
        """
        # Create and save genomic files and dependent entities
        kwargs_dict = self._create_save_genomic_files()

        # Get genomic files for biospecimen
        biospecimen = Biospecimen.query.first()
        # Delete genomic files
        for gf in biospecimen.genomic_files:
            db.session.delete(gf)
        db.session.commit()

        # Check database

        biospecimen = Biospecimen.query.first()
        self.assertEqual(len(biospecimen.genomic_files), 0)

    def test_cascade_delete_via_biospecimen(self):
        """
        Test delete existing genomic file
        Delete biospecimen to which genomic file belongs
        """
        # Create and save genomic files and dependent entities
        kwargs_dict = self._create_save_genomic_files()

        # Get biospecimen
        biospecimen = Biospecimen.query.first()

        # Delete biospecimen
        db.session.delete(biospecimen)
        db.session.commit()

        # Check database
        assert BiospecimenGenomicFile.query.count() == 0

        for kf_id in kwargs_dict.keys():
            gf = GenomicFile.query.get(kf_id)
            assert gf is not None

    def test_cascade_delete_via_genomic_file(self):
        """
        Test delete existing biospecimen
        Delete genomic file to which biospecimen belongs
        """
        # Create and save genomic files and dependent entities
        kwargs_dict = self._create_save_genomic_files()

        assert GenomicFile.query.count() == 2
        # Get genomic_file
        gf = GenomicFile.query.first()

        # Delete biospecimen
        db.session.delete(gf)
        db.session.commit()

        # Check database
        assert BiospecimenGenomicFile.query.count() == 1

    def test_rollups(self):
        """
        Create two gfs representing two bams, with different sequencing
        experiments:
        gf1 (reads1.bam): se strategy: wgs
        gf2 (reads2.bam): se strategy: wxs

        Create a downstream analysis file:
        gf3 (calls.vcf)

        gf3 should have sequencing_strategies of ['wgs', 'wxs']
        """
        self._create_save_dependents()
        bs = Biospecimen.query.all()[0]

        def gf_se(bs, strategy='wgs'):
            sequencing_center_id = SequencingCenter.query.first().kf_id
            se = {
                'external_id': 'se1',
                'experiment_strategy': strategy,
                'is_paired_end': True,
                'platform': 'platform',
                'sequencing_center_id': sequencing_center_id
            }

            gf = {
                'external_id': 'genomic_file',
                'file_name': 'file',
                'size': (random.randint(MIN_SIZE_MB, MAX_SIZE_MB) *
                         MB_TO_BYTES),
                'data_type': 'submitted aligned reads',
                'file_format': '.cram',
                'urls': ['s3://file'],
                'controlled_access': True,
                'is_harmonized': True,
                'paired_end': 1,
                'reference_genome': 'Test01',
                'hashes': {'md5': str(uuid.uuid4())},
                'availability': 'Immediate Download'
            }

            se = SequencingExperiment(**se)
            db.session.add(se)
            db.session.flush()
            gf = GenomicFile(**gf, sequencing_experiment_id=se.kf_id)
            return gf, se

        gf1, se1 = gf_se(bs, 'wgs')
        gf2, se2 = gf_se(bs, 'wxs')
        gf3, se3 = gf_se(bs)
        db.session.add_all([gf1, gf2, gf3])
        db.session.flush()

        tk = Task(name='mutect2')
        db.session.add_all([tk])
        db.session.flush()

        tg1 = TaskGenomicFile(genomic_file_id=gf1.kf_id,
                              task_id=tk.kf_id,
                              is_input=True)
        tg2 = TaskGenomicFile(genomic_file_id=gf2.kf_id,
                              task_id=tk.kf_id,
                              is_input=True)
        tg3 = TaskGenomicFile(genomic_file_id=gf3.kf_id,
                              task_id=tk.kf_id,
                              is_input=False)
        db.session.add_all([tg1, tg2, tg3])
        db.session.commit()

        assert gf1.experiment_strategies == ['wgs']
        assert gf2.experiment_strategies == ['wxs']

        # TODO: This should be a combination of all input files that this
        # file has been derived from, in this case, 'wgs' and 'wxs'
        # assert set(gf3.experiment_strategy) == {'wxs', 'wgs'}

    # TODO Check that file is not deleted if deletion on indexd fails

    def _create_save_genomic_files(self):
        """
        Create and save genomic files to database
        """
        # Create and save genomic file dependent entities
        self._create_save_dependents()
        se = SequencingExperiment.query.all()[0]
        # Create genomic files
        biospecimen = Biospecimen.query.all()[0]
        kwargs_dict = {}
        for i in range(2):
            kwargs = {
                'external_id': 'genomic_file_{}'.format(i),
                'file_name': 'file_{}'.format(i),
                'size': (random.randint(MIN_SIZE_MB, MAX_SIZE_MB) *
                         MB_TO_BYTES),
                'data_type': 'submitted aligned reads',
                'file_format': '.cram',
                'urls': ['s3://file_{}'.format(i)],
                'controlled_access': True,
                'is_harmonized': True,
                'paired_end': 1,
                'reference_genome': 'Test01',
                'hashes': {'md5': str(uuid.uuid4())},
                'availability': 'Immediate Download'
            }
            # Add genomic file to list in biospecimen
            gf = GenomicFile(**kwargs, sequencing_experiment_id=se.kf_id)
            biospecimen.genomic_files.append(gf)
            db.session.add(gf)
            db.session.flush()
            kwargs['kf_id'] = gf.kf_id
            kwargs_dict[gf.kf_id] = kwargs
        db.session.commit()

        return kwargs_dict

    def _create_save_dependents(self):
        """
        Create and save all genomic file dependent entities to db

        Dependent entities: participant, biospecimens
        """
        # Create study
        study = Study(external_id='phs001')
        # Create participant
        p = Participant(external_id='p1',
                        biospecimens=self._create_biospecimens(),
                        is_proband=True, study=study)
        db.session.add(p)
        db.session.commit()

    def _create_biospecimens(self, total=2):
        """
        Create biospecimens
        """
        # Create Sequencing_center
        sc = SequencingCenter(name='Baylor')
        db.session.add(sc)
        db.session.commit()
        # Create Sequencing_experiment
        se = self._create_experiments(sequencing_center_id=sc.kf_id)
        return [Biospecimen(external_sample_id='s{}'.format(i),
                            analyte_type='dna',
                            sequencing_center_id=sc.kf_id)
                for i in range(total)]

    def _create_experiments(self, total=1, sequencing_center_id=None):
        """
        Create sequencing experiments
        """
        data = {
            'external_id': 'se1',
            'experiment_strategy': 'wgs',
            'is_paired_end': True,
            'platform': 'platform',
            'sequencing_center_id': sequencing_center_id
        }
        se = SequencingExperiment(**data)
        db.session.add(se)
        db.session.commit()
        return se
