import uuid

from sqlalchemy.exc import IntegrityError

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.sample.models import Sample
from dataservice.api.aliquot.models import Aliquot
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.genomic_file.models import GenomicFile
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
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
        self.assertEqual(Sample.query.count(), 2)
        self.assertEqual(Aliquot.query.count(), 4)
        self.assertEqual(SequencingExperiment.query.count(), 4)

        # Create genomic genomic files for just one experiment
        experiment = SequencingExperiment.query.all()[0]
        kf_id = experiment.kf_id
        kwargs_dict = {}
        for i in range(2):
            kwargs = {
                'file_name': 'file_{}'.format(i),
                'data_type': 'submitted aligned read',
                'file_format': '.cram',
                'file_url': 's3://file_{}'.format(i),
                'md5sum': str(uuid.uuid4()),
                'controlled_access': True,
                'sequencing_experiment_id': experiment.kf_id
            }
            kwargs_dict[kwargs['md5sum']] = kwargs
            # Add genomic file to db session
            db.session.add(GenomicFile(**kwargs))
        db.session.commit()

        # Check database
        experiment = SequencingExperiment.query.filter_by(
            kf_id=kf_id).one()
        self.assertEqual(len(experiment.genomic_files), 2)

        # Check all input field values with persisted field values
        # for each genomic file
        for _md5sum, kwargs in kwargs_dict.items():
            gf = GenomicFile.query.filter_by(md5sum=_md5sum).one()
            for k, v in kwargs.items():
                self.assertEqual(getattr(gf, k), v)

    def test_create_via_experiment(self):
        """
        Test create genomic file
        """
        # Create and save genomic files and dependent entities
        experiment_id, kwargs_dict = self._create_save_genomic_files()

        # Check database
        experiment = SequencingExperiment.query.filter_by(
            kf_id=experiment_id).one()

        # Check number created files
        self.assertEqual(len(experiment.genomic_files), 2)

        # Check all input field values with persisted field values
        # for each genomic file
        for _md5sum, kwargs in kwargs_dict.items():
            gf = GenomicFile.query.filter_by(md5sum=_md5sum).one()
            for k, v in kwargs.items():
                self.assertEqual(getattr(gf, k), v)

    def test_update(self):
        """
        Test update genomic file
        """
        # Create and save genomic files and dependent entities
        experiment_id, kwargs_dict = self._create_save_genomic_files()

        # Update fields
        kwargs = kwargs_dict[list(kwargs_dict.keys())[0]]
        kwargs['file_name'] = 'updated file name'
        kwargs['data_type'] = 'updated data type'
        gf = GenomicFile.query.filter_by(md5sum=kwargs['md5sum']).one()
        [setattr(gf, k, v)
         for k, v in kwargs.items()]
        db.session.commit()

        # Check database
        gf = GenomicFile.query.filter_by(md5sum=kwargs['md5sum']).one()
        [self.assertEqual(getattr(gf, k), v)
         for k, v in kwargs.items()]

    def test_delete(self):
        """
        Test delete existing genomic file
        """
        # Create and save genomic files and dependent entities
        experiment_id, kwargs_dict = self._create_save_genomic_files()

        # Get genomic files for experiment
        experiment = SequencingExperiment.query.filter_by(
            kf_id=experiment_id).one()

        # Delete genomic files
        for gf in experiment.genomic_files:
            db.session.delete(gf)
        db.session.commit()

        # Check database
        experiment = SequencingExperiment.query.filter_by(
            kf_id=experiment_id).one()
        self.assertEqual(len(experiment.genomic_files), 0)

    def test_delete_via_experiment(self):
        """
        Test delete existing genomic file

        Delete sequencing experiment to which genomic file belongs
        """
        # Create and save genomic files and dependent entities
        experiment_id, kwargs_dict = self._create_save_genomic_files()

        # Get genomic files for experiment
        experiment = SequencingExperiment.query.filter_by(
            kf_id=experiment_id).one()

        # Delete experiment
        db.session.delete(experiment)
        db.session.commit()

        # Check database
        for gf_md5sum in kwargs_dict.keys():
            gf = GenomicFile.query.filter_by(md5sum=gf_md5sum).one_or_none()
            self.assertIs(gf, None)

    def test_not_null_constraint(self):
        """
        Test that a genomic file cannot be created without required parameters
        such as sequencing_experiment_id
        """
        # Create genomic file without foreign key_
        gf = GenomicFile()
        self.assertRaises(IntegrityError, db.session.add(gf))

    def test_foreign_key_constraint(self):
        """
        Test that a genomic file cannot be created without an existing
        sequencing experiment
        """
        # Create genomic file without foreign key_
        gf = GenomicFile(**{'sequencing_experiment_id': ''})
        self.assertRaises(IntegrityError, db.session.add(gf))

    def _create_save_genomic_files(self):
        """
        Create and save genomic files to database
        """
        # Create and save genomic file dependent entities
        self._create_save_dependents()

        # Create genomic genomic files
        experiment = SequencingExperiment.query.all()[0]
        kwargs_dict = {}
        for i in range(2):
            kwargs = {
                'file_name': 'file_{}'.format(i),
                'data_type': 'submitted aligned read',
                'file_format': '.cram',
                'file_url': 's3://file_{}'.format(i),
                'controlled_access': True,
                'md5sum': str(uuid.uuid4())
            }
            kwargs_dict[kwargs['md5sum']] = kwargs
            # Add genomic file to list in experiment
            experiment.genomic_files.append(GenomicFile(**kwargs))
        db.session.commit()

        return experiment.kf_id, kwargs_dict

    def _create_save_dependents(self):
        """
        Create and save all genomic file dependent entities to db

        Dependent entities: participant, samples, aliquots,
        sequencing_experiments
        """
        # Create study
        study = Study(external_id='phs001')

        # Create participant
        p = Participant(external_id='p1', samples=self._create_samples(),
                        is_proband=True, study=study)
        db.session.add(p)
        db.session.commit()

    def _create_samples(self, total=2):
        """
        Create samples with aliquots
        """
        return [Sample(external_id='s{}'.format(i),
                       aliquots=self._create_aliquots())
                for i in range(total)]

    def _create_aliquots(self, total=2):
        """
        Create aliquots with sequencing experiments
        """
        return [Aliquot(external_id='a{}'.format(i),
                        analyte_type='dna',
                        sequencing_experiments=self._create_experiments())
                for i in range(total)]

    def _create_experiments(self, total=1):
        """
        Create sequencing experiments
        """
        data = {
            'external_id': 'se1',
            'experiment_strategy': 'wgs',
            'center': 'broad',
            'is_paired_end': True,
            'platform': 'platform'
        }
        return [SequencingExperiment(**data) for i in range(total)]
