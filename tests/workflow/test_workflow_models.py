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
from dataservice.api.workflow.models import (
    Workflow,
    WorkflowGenomicFile
)
from tests.utils import FlaskTestCase

from unittest.mock import patch, Mock
from tests.mocks import MockIndexd

WORKFLOW_COMMIT_URL = ('https://github.com/kids-first/kf-alignment-workflow/'
                       'commit/0d7f93dff6463446b0ed43dc2883f60c28e6f1f4')


@patch('dataservice.extensions.flask_indexd.requests')
class ModelTest(FlaskTestCase):
    """
    Test Workflow database model
    """

    def test_create_and_find(self, mock):
        """
        Test create workflow
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save workflows and dependents
        participants, workflows = self._create_and_save_workflows()

        GenomicFile.query.limit(5).all()

        # Check database
        # Count checks
        # 4 participants, 2 genomic files per participant
        # 2 workflows, all genomic files are in both workflows
        self.assertEqual(8, GenomicFile.query.count())
        self.assertEqual(2, Workflow.query.count())
        self.assertEqual(16, WorkflowGenomicFile.query.count())
        self.assertEqual(8, WorkflowGenomicFile.query.filter_by(
            is_input=False).count())
        self.assertEqual(8, WorkflowGenomicFile.query.filter_by(
            is_input=True).count())
        # Workflow content checks
        for p in participants:
            gfs = (p.biospecimens[0].genomic_files)
            for gf in gfs:
                gf_workflows = [wgf.workflow
                                for wgf in gf.workflow_genomic_files]
                for gf_workflow in gf_workflows:
                    self.assertIn(gf_workflow, workflows)
                    self.assertEqual(True,
                                     (gf_workflow.name == 'kf-alignment1'
                                      or gf_workflow.name == 'kf-alignment2'))
                    self.assertEqual(WORKFLOW_COMMIT_URL,
                                     gf_workflow.github_commit_url)

    def test_update(self, mock):
        """
        Test update workflow
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save workflows and dependents
        participants, workflows = self._create_and_save_workflows()
        se = SequencingExperiment.query.all()[0]
        # Create new genomic_file
        p0 = Participant.query.filter_by(external_id='Fred').one()
        gf_new = GenomicFile(data_type='slide_image',
                             file_name='slide_image1',
                             sequencing_experiment_id=se.kf_id)
        (p0.biospecimens[0].genomic_files.append(gf_new))
        db.session.commit()

        # Unlink workflow from a genomic file and link to a new one
        wgf = WorkflowGenomicFile.query.first()
        w_id = wgf.workflow_id
        gf_id = wgf.genomic_file_id

        wgf.genomic_file_id = gf_new.kf_id
        db.session.commit()

        # Check database
        w = Workflow.query.get(w_id)
        gf = GenomicFile.query.get(gf_id)
        self.assertNotIn(gf, w.genomic_files)
        self.assertIn(gf_new, w.genomic_files)
        self.assertEqual(9, GenomicFile.query.count())
        self.assertEqual(16, WorkflowGenomicFile.query.count())

    def test_delete(self, mock):
        """
        Test delete workflow
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save workflows and dependents
        participants, workflows = self._create_and_save_workflows()
        kf_id = workflows[0].kf_id

        # Delete workflow
        w = Workflow.query.get(kf_id)
        db.session.delete(w)
        db.session.commit()

        # Check database
        self.assertEqual(0, WorkflowGenomicFile.query.
                         filter_by(workflow_id=kf_id).count())
        self.assertEqual(1, Workflow.query.count())
        self.assertNotIn(workflows[0], Workflow.query.all())
        self.assertEqual(8, GenomicFile.query.count())

    def test_delete_relations(self, mock):
        """
        Test delete GenomicFile and WorkflowGenomicFile
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save workflows and dependents
        participants, workflows = self._create_and_save_workflows()

        # Delete genomic file
        p0 = Participant.query.filter_by(external_id='Fred').one()
        gf = (p0.biospecimens[0].genomic_files[0])
        # Save id and related workflows
        kf_id = gf.kf_id
        gf_workflows = [wgf.workflow
                        for wgf in WorkflowGenomicFile.query.filter_by(
                            genomic_file_id=kf_id)]
        db.session.delete(gf)
        db.session.commit()

        # Check database
        # Genomic file deleted
        self.assertEqual(7, GenomicFile.query.count())
        self.assertEqual(14, WorkflowGenomicFile.query.count())
        self.assertNotIn(gf, (p0.biospecimens[0].genomic_files))
        for w in gf_workflows:
            self.assertNotIn(gf, w.genomic_files)

        # Delete WorkflowGenomicFile
        wgf = WorkflowGenomicFile.query.first()
        kf_id = wgf.kf_id
        w_id = wgf.workflow_id
        gf_id = wgf.genomic_file_id
        db.session.delete(wgf)
        db.session.commit()

        # Check database
        # No genomic files or workflows were deleted
        self.assertEqual(7, GenomicFile.query.count())
        self.assertEqual(2, Workflow.query.count())
        # Association deleted
        self.assertEqual(None, WorkflowGenomicFile.query.get(kf_id))
        # Workflow unlinked from genomic_file
        w = Workflow.query.get(w_id)
        gf = GenomicFile.query.get(gf_id)
        self.assertNotIn(gf, w.genomic_files)

    def test_foreign_key_constraint(self, mock):
        """
        Test that a workflow_genomic_file cannot be created without existing
        reference Workflow and GenomicFile. This checks foreign key constraint
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create study_participant
        data = {
            'is_input': True,
            'workflow_id': 'none',
            'genomic_file_id': 'none'
        }
        wgf = WorkflowGenomicFile(**data)
        db.session.add(wgf)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_not_null_constraint(self, mock):
        """
        Test that a workflow and workflow genomic file cannot be created
        without required parameters

        workflow genomic file requires workflow_id, genomic_file_id, is_input
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save workflows and dependents
        participants, workflows = self._create_and_save_workflows()

        # Missing all required parameters
        data = {}
        wgf = WorkflowGenomicFile(**data)
        db.session.add(wgf)

        # Check database
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Missing 1 required param
        data = {
            'workflow_id': workflows[0].kf_id
        }
        wgf = WorkflowGenomicFile(**data)
        db.session.add(wgf)

        # Check database
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_unique_constraint(self, mock):
        """
        Test that duplicate tuples (workflow_id, genomic_file_id, is_input)
        cannot be created
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save workflows and dependents
        participants, workflows = self._create_and_save_workflows()

        # Get existing WorkflowGenomicFile
        wgf = WorkflowGenomicFile.query.first()
        w_id = wgf.workflow_id
        gf_id = wgf.genomic_file_id
        is_input = wgf.is_input

        new_wgf = WorkflowGenomicFile(workflow_id=w_id, genomic_file_id=gf_id,
                                      is_input=is_input)
        db.session.add(new_wgf)

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
            'biospecimen_id': biospec_id,
            'sequencing_experiment_id': sequencing_experiment_id
        }
        return GenomicFile(**data)

    def _create_workflow(self, _name, genomic_files=None):
        """
        Create workflow
        """
        data = {
            'task_id': 'task_{}'.format(_name),
            'name': _name,
            'github_commit_url': WORKFLOW_COMMIT_URL
        }
        if genomic_files:
            data['genomic_files'] = genomic_files
        return Workflow(**data)

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
            gf_in = self._create_genomic_file('gf_{}_in'.format(i),
                                              biospec_id=s.kf_id,
                                              sequencing_experiment_id=se.kf_id)
            # Output GF
            gf_out = self._create_genomic_file('gf_{}_out'.format(i),
                                               data_type='aligned read',
                                               biospec_id=s.kf_id,
                                               sequencing_experiment_id=\
                                                                    se.kf_id)
            s.genomic_files = [gf_in, gf_out]
            p.biospecimens=[s]
            participants.append(p)

        return participants

    def _create_and_save_workflows(self):
        """
        Create and save workflows + dependent entities
        """
        # Create participants and dependent entities
        participants = self._create_participants_and_dependents()
        db.session.add_all(participants)
        db.session.commit()

        # Create workflow
        w1 = self._create_workflow('kf-alignment1')
        w2 = self._create_workflow('kf-alignment2')
        workflows = [w1, w2]

        # Add genomic files to workflows
        # Each participant has an input GF and output GF
        for p in participants:
            gfs = (p.biospecimens[0].genomic_files)
            # Add input and output genomic files to both workflows
            for w in workflows:
                for gf in gfs:
                    # Input gf
                    if gf.data_type == 'submitted aligned read':
                        # Must use assoc obj to add
                        wgf = WorkflowGenomicFile(workflow=w,
                                                  genomic_file=gf,
                                                  is_input=True)
                        db.session.add(wgf)
                    # Output gf
                    else:
                        # Use assoc proxy to add, is_input=False by default
                        w.genomic_files.append(gf)

                db.session.add(w)
        db.session.commit()

        return participants, workflows
