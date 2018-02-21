from sqlalchemy.exc import IntegrityError

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.study.models import Study
from dataservice.api.investigator.models import Investigator
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test investigator database model
    """

    def test_create_and_find(self):
        """
        Test create investigator
        """
        # Create studies and investigator
        studies, investigator, kwargs = self.create_investigator()

        # Check database
        # Counts
        self.assertEqual(2, Study.query.count())
        self.assertEqual(1, Investigator.query.count())
        # Study content
        for k, v in kwargs.items():
            self.assertEqual(v, getattr(studies[1], k))
        # investigator studies
        for s in studies:
            print(s.kf_id)
            print(studies)
            print(investigator)
            self.assertEqual(investigator.studies, studies)

    def test_update(self):
        """
        Test update investigator
        """
        # Create studies and investigator
        studies, investigator, kwargs = self.create_investigator()

        # Add new study to investigator
        s_new = Study(external_id='phs002', investigator_id=investigator.kf_id)
        db.session.add(s_new)
        db.session.commit()

        # Check database
        self.assertEqual(3,
                         len(Investigator.query.get(
                                                    investigator.kf_id).studies))
        self.assertIn(s_new, Investigator.query.get(investigator.kf_id).studies)

        # Add study to new investigator
        i = Investigator(name='Alma')
        i.studies = [s_new]
        db.session.commit()

        # Check database
        self.assertEqual(i.studies[0].kf_id,
                         Study.query.filter_by(
                             external_id='phs002').one().kf_id)
        self.assertNotIn(i, Investigator.query.get(investigator.kf_id).studies)

    def test_delete(self):
        """
        Test delete investigator
        """
        # Create studies and investigator
        studies, investigator, kwargs = self.create_investigator()

        # Delete investigator
        kf_id = investigator.kf_id
        db.session.delete(investigator)
        db.session.commit()

        # Check database
        self.assertEqual(None, Investigator.query.get(kf_id))
        # study can exist without investigator
        self.assertEqual(2, Study.query.count())

    def test_delete_relations(self):
        """
        Test delete study from Investigator
        """
        # Create studies and investigator
        studies, investigator, kwargs = self.create_investigator()

        # Delete study from investigator
        s0 = studies[0]
        del investigator.studies[0]
        db.session.commit()

        # Check database
        self.assertNotIn(s0, Investigator.query.get(investigator.kf_id).studies)

    def test_foreign_key_constraint(self):
        """
        Test that a investigator can be created without existing
        reference Study. This checks foreign key constraint
        """
        # Create investigator
        i = Investigator(name='Adam', institution='CHOP')
        db.session.add(i)
        db.session.commit()
        # Check for database
        self.assertEqual(1, Investigator.query.count())

    def create_investigator(self):
        # Create investigator
        investigator = Investigator(name='Adam', institution='CHOP')
                        
        # Create studies
        studies = []
        for i in range(2):
            kwargs = {
                'attribution': ('https://dbgap.ncbi.nlm.nih.gov/'
                            'aa/wga.cgi?view_pdf&stacc=phs000178.v9.p8'),
                'external_id': 'phs00{}'.format(i),
                'name': 'study_{}'.format(i),
                'version': 'v1'
            }
            studies.append(Study(**kwargs))

        # Add study to investigator
        investigator.studies.extend(studies)
        db.session.add(investigator)
        db.session.commit()

        return studies, investigator, kwargs
