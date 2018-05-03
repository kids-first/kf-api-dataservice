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
        # Create genomic genomic files for just one biospecimen
        biospecimen = Biospecimen.query.all()[0]
        kf_id = biospecimen.kf_id
        # Properties keyed on kf_id
        kwargs_dict = {}
        for i in range(2):
            kwargs = {
                'external_id': 'genomic_file_{}'.format(i),
                'file_name': 'file_{}'.format(i),
                'data_type': 'submitted aligned read',
                'file_format': '.cram',
                'urls': ['s3://file_{}'.format(i)],
                'hashes': {'md5': str(uuid.uuid4())},
                'controlled_access': True,
                'is_harmonized': True,
                'reference_genome': 'Test01',
                'availability': 'availble for download',
                'biospecimen_id': biospecimen.kf_id,
                'sequencing_experiment_id': se.kf_id
            }
            # Add genomic file to db session
            gf = GenomicFile(**kwargs)
            db.session.add(gf)
            db.session.flush()
            kwargs['kf_id'] = gf.kf_id
            kwargs_dict[kwargs['kf_id']] = kwargs
        db.session.commit()

        # Check database
        biospecimen = Biospecimen.query.filter_by(
            kf_id=kf_id).one()
        self.assertEqual(len(biospecimen.genomic_files), 2)

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

    def test_create_via_biospecimen(self):
        """
        Test create genomic file
        """
        # Create and save genomic files and dependent entities
        biospecimen_id, kwargs_dict = self._create_save_genomic_files()

        # Check database
        biospecimen = Biospecimen.query.filter_by(
            kf_id=biospecimen_id).one()

        # Check number created files
        self.assertEqual(len(biospecimen.genomic_files), 2)

        # Check all input field values with persisted field values
        # for each genomic file
        self.indexd.Session().get.side_effect = None
        for kf_id, kwargs in kwargs_dict.items():
            # Mock out the response from indexd for the file
            mock_file = {
                'file_name': kwargs['file_name'],
                'urls': kwargs['urls'],
                'hashes': kwargs['hashes'],
                'size': kwargs['size']
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
        biospecimen_id, kwargs_dict = self._create_save_genomic_files()

        # Update fields
        kwargs = kwargs_dict[list(kwargs_dict.keys())[0]]
        kwargs['file_name'] = 'updated file name'
        kwargs['data_type'] = 'updated data type'
        gf = GenomicFile.query.get(kwargs['kf_id'])
        [setattr(gf, k, v)
         for k, v in kwargs.items()]
        db.session.commit()

        # Check database
        gf = GenomicFile.query.get(kwargs['kf_id'])
        [self.assertEqual(getattr(gf, k), v)
         for k, v in kwargs.items()]

    def test_delete(self):
        """
        Test delete existing genomic file
        """
        # Create and save genomic files and dependent entities
        biospecimen_id, kwargs_dict = self._create_save_genomic_files()

        # Get genomic files for biospecimen
        biospecimen = Biospecimen.query.filter_by(
            kf_id=biospecimen_id).one()

        # Delete genomic files
        for gf in biospecimen.genomic_files:
            db.session.delete(gf)
        db.session.commit()

        # Check database
        biospecimen = Biospecimen.query.filter_by(
            kf_id=biospecimen_id).one()
        self.assertEqual(len(biospecimen.genomic_files), 0)

    def test_delete_via_biospecimen(self):
        """
        Test delete existing genomic file

        Delete biospecimen to which genomic file belongs
        """
        # Create and save genomic files and dependent entities
        biospecimen_id, kwargs_dict = self._create_save_genomic_files()

        # Get genomic files for biospecimen
        biospecimen = Biospecimen.query.filter_by(
            kf_id=biospecimen_id).one()

        # Delete biospecimen
        db.session.delete(biospecimen)
        db.session.commit()

        # Check database
        assert GenomicFile.query.count() == 0

        for kf_id in kwargs_dict.keys():
            gf = GenomicFile.query.get(kf_id)
            assert gf is None

        # Check that indexd was called successfully
        assert self.indexd.Session().delete.call_count == 2

    # TODO Check that file is not deleted if deletion on indexd fails

    def test_foreign_key_constraint(self):
        """
        Test that a genomic file cannot be created without an existing
        biospecimen
        """
        # Create genomic file without foreign key_
        gf = GenomicFile(**{'biospecimen_id': ''})
        self.assertRaises(IntegrityError, db.session.add(gf))

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
                'data_type': 'submitted aligned read',
                'file_format': '.cram',
                'urls': ['s3://file_{}'.format(i)],
                'controlled_access': True,
                'is_harmonized': True,
                'reference_genome': 'Test01',
                'hashes': {'md5': uuid.uuid4()},
                'availability': 'availble for download'
            }
            # Add genomic file to list in biospecimen
            gf = GenomicFile(**kwargs, sequencing_experiment_id=se.kf_id)
            biospecimen.genomic_files.append(gf)
            db.session.flush()
            kwargs['kf_id'] = gf.kf_id
            kwargs_dict[gf.kf_id] = kwargs
        db.session.commit()

        return biospecimen.kf_id, kwargs_dict

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
