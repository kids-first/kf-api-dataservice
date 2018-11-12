import uuid
import random
from sqlalchemy.exc import IntegrityError

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.task.models import (
    Task,
    TaskGenomicFile
)
from tests.utils import FlaskTestCase

from unittest.mock import patch
from tests.mocks import MockIndexd


@patch('dataservice.extensions.flask_indexd.requests')
class ModelTest(FlaskTestCase):
    """
    Test Task database model
    """

    def test_create_and_find(self, mock):
        """
        Test create task
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save tasks and dependents
        participants, tasks = self._create_and_save_tasks()

        GenomicFile.query.limit(5).all()

        # Check database
        # Count checks
        # 4 participants, 2 genomic files per participant
        # 2 tasks, all genomic files are in both tasks
        self.assertEqual(8, GenomicFile.query.count())
        self.assertEqual(2, Task.query.count())
        self.assertEqual(16, TaskGenomicFile.query.count())
        self.assertEqual(8, TaskGenomicFile.query.filter_by(
            is_input=False).count())
        self.assertEqual(8, TaskGenomicFile.query.filter_by(
            is_input=True).count())
        # Task content checks
        for p in participants:
            gfs = (p.biospecimens[0].genomic_files)
            for gf in gfs:
                gf_tasks = [
                    tgf.task
                    for tgf in gf.task_genomic_files]
                for gf_task in gf_tasks:
                    self.assertIn(gf_task, tasks)
                    self.assertEqual(
                        True,
                        (gf_task.name == 'kf-alignment1'
                         or gf_task.name == 'kf-alignment2'))

    def test_update(self, mock):
        """
        Test update task
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save tasks and dependents
        participants, tasks = self._create_and_save_tasks()
        se = SequencingExperiment.query.all()[0]
        # Create new genomic_file
        p0 = Participant.query.filter_by(external_id='Fred').one()
        gf_new = GenomicFile(data_type='slide_image',
                             file_name='slide_image1',
                             sequencing_experiment_id=se.kf_id)
        (p0.biospecimens[0].genomic_files.append(gf_new))
        db.session.commit()

        # Unlink task from a genomic file and link to a new one
        tgf = TaskGenomicFile.query.first()
        t_id = tgf.task_id
        gf_id = tgf.genomic_file_id

        tgf.genomic_file_id = gf_new.kf_id
        db.session.commit()

        # Check database
        t = Task.query.get(t_id)
        gf = GenomicFile.query.get(gf_id)
        self.assertNotIn(gf, t.genomic_files)
        self.assertIn(gf_new, t.genomic_files)
        self.assertEqual(9, GenomicFile.query.count())
        self.assertEqual(16, TaskGenomicFile.query.count())

    def test_delete(self, mock):
        """
        Test delete task
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save tasks and dependents
        participants, tasks = self._create_and_save_tasks()
        kf_id = tasks[0].kf_id

        # Delete task
        t = Task.query.get(kf_id)
        db.session.delete(t)
        db.session.commit()

        # Check database
        self.assertEqual(0, TaskGenomicFile.query.
                         filter_by(task_id=kf_id).count())
        self.assertEqual(1, Task.query.count())
        self.assertNotIn(tasks[0], Task.query.all())
        self.assertEqual(8, GenomicFile.query.count())

    def test_delete_relations(self, mock):
        """
        Test delete GenomicFile and TaskGenomicFile
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save tasks and dependents
        participants, tasks = self._create_and_save_tasks()

        # Delete genomic file
        p0 = Participant.query.filter_by(external_id='Fred').one()
        gf = (p0.biospecimens[0].genomic_files[0])
        # Save id and related tasks
        kf_id = gf.kf_id
        gf_tasks = [
            tgf.task
            for tgf in TaskGenomicFile.query.filter_by(
                genomic_file_id=kf_id)]
        db.session.delete(gf)
        db.session.commit()

        # Check database
        # Genomic file deleted
        self.assertEqual(7, GenomicFile.query.count())
        self.assertEqual(14, TaskGenomicFile.query.count())
        self.assertNotIn(gf, (p0.biospecimens[0].genomic_files))
        for t in gf_tasks:
            self.assertNotIn(gf, t.genomic_files)

        # Delete TaskGenomicFile
        tgf = TaskGenomicFile.query.first()
        kf_id = tgf.kf_id
        t_id = tgf.task_id
        gf_id = tgf.genomic_file_id
        db.session.delete(tgf)
        db.session.commit()

        # Check database
        # No genomic files or tasks were deleted
        self.assertEqual(7, GenomicFile.query.count())
        self.assertEqual(2, Task.query.count())
        # Association deleted
        self.assertEqual(None, TaskGenomicFile.query.get(kf_id))
        # Task unlinked from genomic_file
        t = Task.query.get(t_id)
        gf = GenomicFile.query.get(gf_id)
        self.assertNotIn(gf, t.genomic_files)

    def test_foreign_key_constraint(self, mock):
        """
        Test that a task_genomic_file cannot be created without
        existing reference Task and GenomicFile.
        This checks foreign key constraint
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create study_participant
        data = {
            'is_input': True,
            'task_id': 'none',
            'genomic_file_id': 'none'
        }
        tgf = TaskGenomicFile(**data)
        db.session.add(tgf)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_not_null_constraint(self, mock):
        """
        Test that a task and task genomic file cannot be
        created without required parameters

        task genomic file requires task_id,
        genomic_file_id, is_input
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save tasks and dependents
        participants, tasks = self._create_and_save_tasks()

        # Missing all required parameters
        data = {}
        tgf = TaskGenomicFile(**data)
        db.session.add(tgf)

        # Check database
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Missing 1 required param
        data = {
            'task_id': tasks[0].kf_id
        }
        tgf = TaskGenomicFile(**data)
        db.session.add(tgf)

        # Check database
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_unique_constraint(self, mock):
        """
        Test that duplicate tuples
        (task_id, genomic_file_id, is_input)
        cannot be created
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save tasks and dependents
        participants, tasks = self._create_and_save_tasks()

        # Get existing TaskGenomicFile
        tgf = TaskGenomicFile.query.first()
        t_id = tgf.task_id
        gf_id = tgf.genomic_file_id
        is_input = tgf.is_input

        new_tgf = TaskGenomicFile(task_id=t_id,
                                   genomic_file_id=gf_id,
                                   is_input=is_input)
        db.session.add(new_tgf)

        # Check database
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def _create_biospecimen(self, _id, genomic_files=None,
                            sequencing_center_id=None,
                            participant_id=None):
        """
        Create biospecimen with genomic_files
        """
        bs = Biospecimen(external_sample_id=_id, analyte_type='dna',
                         genomic_files=genomic_files or [],
                         sequencing_center_id=sequencing_center_id,
                         participant_id=participant_id)
        db.session.add(bs)
        db.session.commit()
        return bs

    def _create_experiment(self, _id, genomic_files=None,
                           sequencing_center_id=None):
        """
        Create sequencing experiment
        """
        data = {
            'external_id': _id,
            'experiment_strategy': 'wgs',
            'is_paired_end': True,
            'platform': 'platform',
            'genomic_files': genomic_files or [],
            'sequencing_center_id': sequencing_center_id
        }
        se = SequencingExperiment(**data)
        db.session.add(se)
        db.session.commit()
        return se

    def _create_genomic_file(self, _id, data_type='submitted aligned read',
                             sequencing_experiment_id=None, biospec_id=None):
        """
        Create genomic file
        """
        data = {
            'file_name': 'file_{}'.format(_id),
            'data_type': data_type,
            'file_format': '.cram',
            'urls': ['s3://file_{}'.format(_id)],
            'hashes': {'md5': str(uuid.uuid4())},
            'sequencing_experiment_id': sequencing_experiment_id
        }
        return GenomicFile(**data)

    def _create_task(self, _name, genomic_files=None):
        """
        Create task
        """
        data = {
            'external_task_id': str(uuid.uuid4()),
            'name': _name,
        }
        if genomic_files:
            data['genomic_files'] = genomic_files
        return Task(**data)

    def _create_participants_and_dependents(self):
        """
        Create participant with required entities
        """
        # Create study
        study = Study(external_id='phs001')

        names = ['Fred', 'Wilma', 'Pebbles', 'Dino']
        proband = [True, False]
        participants = []
        for i, _name in enumerate(names):
            # Participants
            p = Participant(external_id=_name,
                            is_proband=random.choice(proband),
                            study=study)
            db.session.add(p)
            db.session.commit()
            # Sequencing center
            sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
            if sc is None:
                sc = SequencingCenter(name="Baylor")
                db.session.add(sc)
                db.session.commit()
            # SequencingExperiment
            se = self._create_experiment('se_{}'.format(i),
                                         sequencing_center_id=sc.kf_id)
            # Biospecimen
            s = self._create_biospecimen('s_{}'.format(i),
                                         sequencing_center_id=sc.kf_id,
                                         participant_id=p.kf_id)
            # Input GF
            gf_in = self._create_genomic_file(
                'gf_{}_in'.format(i),
                sequencing_experiment_id=se.kf_id)
            # Output GF
            gf_out = self._create_genomic_file(
                'gf_{}_out'.format(i),
                data_type='aligned read',
                sequencing_experiment_id=se.kf_id)

            s.genomic_files = [gf_in, gf_out]
            p.biospecimens = [s]
            participants.append(p)

        return participants

    def _create_and_save_tasks(self):
        """
        Create and save tasks + dependent entities
        """
        # Create participants and dependent entities
        participants = self._create_participants_and_dependents()
        db.session.add_all(participants)
        db.session.commit()

        # Create task
        t1 = self._create_task('kf-alignment1')
        t2 = self._create_task('kf-alignment2')
        tasks = [t1, t2]

        # Add genomic files to tasks
        # Each participant has an input GF and output GF
        for p in participants:
            gfs = (p.biospecimens[0].genomic_files)
            # Add input and output genomic files to both tasks
            for t in tasks:
                for gf in gfs:
                    # Input gf
                    if gf.data_type == 'submitted aligned read':
                        # Must use assoc obj to add
                        tgf = TaskGenomicFile(task=t,
                                               genomic_file=gf,
                                               is_input=True)
                        db.session.add(tgf)
                    # Output gf
                    else:
                        # Use assoc proxy to add, is_input=False by default
                        t.genomic_files.append(gf)

                db.session.add(t)
        db.session.commit()

        return participants, tasks
