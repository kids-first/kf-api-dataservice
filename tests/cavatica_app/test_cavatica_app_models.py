import uuid

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.cavatica_task.models import CavaticaTask
from dataservice.api.cavatica_app.models import CavaticaApp
from tests.utils import FlaskTestCase

from unittest.mock import patch
from tests.mocks import MockIndexd

CAVATICA_APP_COMMIT_URL = (
    'https://github.com/kids-first/kf-alignment-cavatica_task/'
    'commit/0d7f93dff6463446b0ed43dc2883f60c28e6f1f4')


@patch('dataservice.extensions.flask_indexd.requests')
class ModelTest(FlaskTestCase):
    """
    Test CavaticaApp database model
    """

    def test_create_and_find(self, mock):
        """
        Test create cavatica_app
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put
        # Create and save cavatica_app and dependents
        data = self._create_and_save_cavatica_app()

        # Check database
        assert 1 == CavaticaApp.query.count()
        a = CavaticaApp.query.first()
        for k, v in data.items():
            if k == '_obj':
                continue
            assert v == getattr(a, k)
        assert 2 == len(a.cavatica_tasks)

    def test_update(self, mock):
        """
        Test update cavatica_app
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        # Create and save cavatica_tasks and dependents
        data = self._create_and_save_cavatica_app()
        a = CavaticaApp.query.first()
        a.cavatica_tasks.pop()
        a.name = 'app1'
        db.session.commit()

        # Check database
        a = CavaticaApp.query.first()
        assert 1 == len(a.cavatica_tasks)
        assert 'app1' == a.name

    def test_delete(self, mock):
        """
        Test delete cavatica_app
        """
        indexd = MockIndexd()
        mock.Session().post = indexd.post
        mock.Session().get = indexd.get
        mock.Session().put = indexd.put

        # Create and save cavatica_tasks and dependents
        data = self._create_and_save_cavatica_app()
        a = CavaticaApp.query.first()
        db.session.delete(a)

        # Check database
        assert 0 == CavaticaApp.query.count()
        assert 2 == CavaticaTask.query.count()

    def _create_cavatica_task(self, _name, genomic_files=None):
        """
        Create cavatica_task
        """
        data = {
            'external_cavatica_task_id': str(uuid.uuid4()),
            'name': _name,
        }
        if genomic_files:
            data['genomic_files'] = genomic_files
        return CavaticaTask(**data)

    def _create_participants_and_dependents(self):
        """
        Create participant with required entities
        """
        # Sequencing center
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()

        # Create study
        study = Study(external_id='phs001')

        # Participants
        p = Participant(external_id='p0',
                        is_proband=True,
                        study=study)

        # Biospecimen
        bs = Biospecimen(analyte_type='dna',
                         sequencing_center=sc,
                         participant=p)

        # SequencingExperiment
        data = {
            'external_id': 'se',
            'experiment_strategy': 'wgs',
            'is_paired_end': True,
            'platform': 'platform',
            'sequencing_center': sc
        }
        se = SequencingExperiment(**data)

        # Genomic Files
        genomic_files = []
        for i in range(4):
            data = {
                'file_name': 'gf_{}'.format(i),
                'data_type': 'submitted aligned read',
                'file_format': '.cram',
                'urls': ['s3://file_{}'.format(i)],
                'hashes': {'md5': str(uuid.uuid4())}
            }
            gf = GenomicFile(**data)
            bs.genomic_files.append(gf)
            se.genomic_files.append(gf)
            genomic_files.append(gf)

        db.session.add(study)
        db.session.commit()

        return genomic_files

    def _create_and_save_cavatica_app(self):
        """
        Create and save cavatica_app + dependent entities
        """
        gfs = self._create_participants_and_dependents()

        ct1 = self._create_cavatica_task('ct1',
                                         genomic_files=gfs[0:2])
        ct2 = self._create_cavatica_task('ct2',
                                         genomic_files=gfs[2:])
        cavatica_tasks = [ct1, ct2]

        data = {
            'external_cavatica_app_id': 'app1',
            'name': 'ImAwsammmmm',
            'revision': 1,
            'github_commit_url': CAVATICA_APP_COMMIT_URL,
            'cavatica_tasks': cavatica_tasks
        }
        app = CavaticaApp(**data)

        db.session.add(app)
        db.session.commit()

        data['_obj'] = app

        return data
