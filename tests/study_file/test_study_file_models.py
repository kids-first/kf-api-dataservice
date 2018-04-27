from sqlalchemy.exc import IntegrityError

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.study_file.models import StudyFile
from tests.utils import IndexdTestCase


class ModelTest(IndexdTestCase):
    """
    Test StudyFile database model
    """

    def test_create_and_find(self):
        """
        Test create study_file
        """
        # Create study_files and study
        study_files, study, data = self.create_study_file()
        # Check database
        # Counts
        self.assertEqual(1, Study.query.count())
        self.assertEqual(3, StudyFile.query.count())
        # Study content
        for k, v in data.items():
            self.assertEqual(v, getattr(study, k))
        # study studyfiles
        self.assertEqual(study.study_files, study_files)

    def test_update(self):
        """
        Test update study_file
        """
        # Create study_files and study
        study_files, study, data = self.create_study_file()

        # Add new study_file to study
        sf_new = StudyFile(file_name='file_3',
                           study_id=study.kf_id,
                           availability='available for download')
        db.session.add(sf_new)
        db.session.commit()

        # Check database
        self.assertEqual(4, len(Study.query.get(study.kf_id).study_files))
        self.assertIn(sf_new, Study.query.get(study.kf_id).study_files)

        # Change study_file's study
        s = Study(external_id='phs002')
        sf0 = study_files[0]
        sf0.study = s
        db.session.commit()

        # Check database
        self.assertEqual(sf0.study.kf_id,
                         Study.query.filter_by(
                             external_id='phs002').one().kf_id)
        self.assertNotIn(sf0, Study.query.get(study.kf_id).study_files)

    def test_delete(self):
        """
        Test delete study_file
        """
        # Create study_files and study
        study_files, study, data = self.create_study_file()

        # Delete study
        kf_id = study.kf_id
        db.session.delete(study)
        db.session.commit()

        # Check database
        self.assertEqual(None, Study.query.get(kf_id))
        self.assertEqual(0, StudyFile.query.count())

    def test_delete_relations(self):
        """
        Test delete study_file from Study
        """
        # Create study_files and study
        study_files, study, data = self.create_study_file()

        # Delete study_file from study
        sf0 = study_files[0]
        del sf0.study
        db.session.commit()

        # Check database
        self.assertNotIn(sf0, Study.query.get(study.kf_id).study_files)

    def test_foreign_key_constraint(self):
        """
        Test that a study_file cannot be created without existing
        reference Study. This checks foreign key constraint
        """
        # Create participant
        sf = StudyFile(file_name='file_4')
        db.session.add(sf)

        # Check for exception
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_not_null_constraint(self):
        """
        Test that a study_file cannot be created without required parameters

        study_file requires study_id
        """
        # Create study
        data = {}
        db.session.add(StudyFile(**data))

        # Check for exception
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Check database
        self.assertEqual(0, StudyFile.query.count())

    def create_study_file(self):
        # Create study
        data = {
            'attribution': ('https://dbgap.ncbi.nlm.nih.gov/'
                            'aa/wga.cgi?view_pdf&stacc=phs000178.v9.p8'),
            'external_id': 'phs001',
            'name': 'study1',
            'version': 'v1'
        }
        study = Study(**data)

        # Create study_files
        study_files = []
        for i in range(3):
            kwargs = {
                'external_id': 'test_study_file_{}'.format(i),
                'file_name': 'file_{}'.format(i),
                'availability': 'available for download',
                'study_id': study.kf_id
            }
            study_files.append(StudyFile(**kwargs))
        # Add study_files to study
        study.study_files.extend(study_files)
        db.session.add(study)
        db.session.commit()

        return study_files, study, data
