from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.phenotype.models import Phenotype
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError


class ModelTest(FlaskTestCase):
    """
    Test Phenotype database model
    """

    def test_create_and_find(self):
        """
        Test create phenotype
        """
        dt = datetime.now()
        # Create Study
        study = Study(external_id='phs001')

        # Create and save participant
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id, is_proband=True,
                        study=study)
        db.session.add(p)
        db.session.commit()
        kwarg_dict = {}
        # Create phenotypes
        for i in range(2):
            data = {
                'external_id': 'test_phenotype_{}'.format(i),
                'source_text_phenotype': 'test phenotype_{}'.format(i),
                'hpo_id_phenotype': 'HP:0000118',
                'snomed_id_phenotype': '38033009',
                'age_at_event_days': 120,
                'participant_id': p.kf_id
                }
            ph = Phenotype(**data)
            kwarg_dict[ph.external_id] = data
            db.session.add(ph)
        db.session.commit()

        self.assertEqual(Phenotype.query.count(), 2)
        for k, kwargs in kwarg_dict.items():
            ph = Phenotype.query.filter_by(external_id=k).one()
            for key, value in kwargs.items():
                self.assertEqual(value, getattr(ph, key))
            self.assertGreater(ph.created_at, dt)
            self.assertGreater(ph.modified_at, dt)
            self.assertIs(type(uuid.UUID(ph.uuid)), uuid.UUID)

    def test_create_via_participant(self):
        """
        create phenotypes via creation of participant
        """
        phenotypes, p, pheno = self._create_phenotypes()

        # Check phenotypes were created
        self.assertEqual(Phenotype.query.count(), 2)

        # Check Particpant has the phenotypes
        for p in Participant.query.first().phenotypes:
            self.assertIn(p.source_text_phenotype, pheno)

        # Phenotypes have the participant
        p = Participant.query.first()
        for ph in Phenotype.query.all():
            self.assertEqual(ph.participant_id, p.kf_id)

    def test_update_phenotype(self):
        """
        Test update phenotype
        """
        phenotypes, p, pheno = self._create_phenotypes()

        # Update and save
        phe = Phenotype.query.filter_by(source_text_phenotype=pheno[0]).\
              one_or_none()
        phen = 'test phenotype 3'
        phe.source_text_phenotype = phen
        db.session.commit()

        # Check updated values
        phe = Phenotype.query.filter_by(source_text_phenotype=phen).\
           one_or_none()
        self.assertIsNot(phe, None)

    def test_delete_phenotype(self):
        """
        Test delete phenotype
        """
        phenotypes, p, pheno = self._create_phenotypes()

        # Choose one and delete it
        ph = Phenotype.query.filter_by(source_text_phenotype=pheno[0]).\
           one_or_none()
        db.session.delete(ph)
        db.session.commit()

        ph = Phenotype.query.filter_by(source_text_phenotype=pheno[0]).\
           one_or_none()
        self.assertIs(ph, None)
        phenotypes = [_ph for _ph in p.phenotypes]
        self.assertNotIn(ph, phenotypes)

    def test_delete_phenotype_via_participant(self):
        """
        Test delete related phenotypes via deletion of participant
        """
        phenotypes, p, pheno = self._create_phenotypes()

        # Delete participant
        db.session.delete(p)
        db.session.commit()

        # Check that phenotypes have been deleted
        ph1 = Phenotype.query.filter_by(source_text_phenotype=pheno[0]).\
           one_or_none()
        ph2 = Phenotype.query.filter_by(source_text_phenotype=pheno[1]).\
           one_or_none()
        self.assertIs(ph1, None)
        self.assertIs(ph2, None)

    def test_not_null_constraint(self):
        """
        Test that a phenotype cannot be created without required
        parameters such as participant_id
        """
        # Create phenotype
        data = {
            'source_text_phenotype': 'phenotype_1',
            # non-existent required param: participant_id
        }
        d = Phenotype(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(d))

    def test_foreign_key_constraint(self):
        """
        Test that a phenotype cannot be created without an existing
        reference Participant. This checks foreign key constraint
        """
        # Create phenotype
        data = {
            'source_text_phenotype': 'phenotype_1',
            'participant_id': ''  # empty blank foreign key
        }
        d = Phenotype(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(d))

    def _create_phenotypes(self):
        """
        Create phenotypes and required entities
        """
        # Create Study
        study = Study(external_id='phs001')

        # Create two phenotypes
        pheno = ['test phenotype 1', 'test phenotype 2']
        ph1 = Phenotype(source_text_phenotype=pheno[0],
                        external_id='test_phenotype_0')
        ph2 = Phenotype(source_text_phenotype=pheno[1],
                        external_id='test_phenotype_0')
        p = Participant(external_id='p1', is_proband=True,
                        study=study)

        # Add to participant and save
        p.phenotypes.extend([ph1, ph2])
        db.session.add(p)
        db.session.commit()

        return [ph1, ph2], p, pheno
