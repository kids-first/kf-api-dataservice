from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.participant.models import Participant
from dataservice.api.phenotype.models import Phenotype
from tests.utils import FlaskTestCase

from sqlalchemy.exc import IntegrityError


class ModelTest(FlaskTestCase):
    """
    Test Phenotype database model
    """

    def test_create(self):
        """
        Test create phenotype
        """
        # Create and save participant
        participant_id = 'Test subject 0'
        p = Participant(external_id=participant_id)
        db.session.add(p)
        db.session.commit()

        # Create phenotypes
        data = {
            'phenotype': 'test phenotype 1',
            'hpo_id': 'HP:0000118',
            'age_at_event_days': 120,
            'participant_id': p.kf_id
        }
        dt = datetime.now()
        ph1 = Phenotype(**data)
        db.session.add(ph1)
        data['phenotype'] = 'phenotype_2'
        data['hpo_id'] = 'HP:0040064'
        ph2 = Phenotype(**data)
        db.session.add(ph2)
        db.session.commit()

        self.assertEqual(Phenotype.query.count(), 2)
        new_phenotype = Phenotype.query.all()[1]
        self.assertGreater(new_phenotype.created_at, dt)
        self.assertGreater(new_phenotype.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_phenotype.uuid)), uuid.UUID)

        self.assertEqual(new_phenotype.phenotype, data['phenotype'])
        self.assertEqual(new_phenotype.hpo_id, 'HP:0040064')

    def test_create_via_participant(self):
        """
        create phenotypes via creation of participant
        """
        # Create two phenotypes
        pheno = ['test phenotype 1', 'test phenotype 2']
        ph1 = Phenotype(phenotype=pheno[0])
        ph2 = Phenotype(phenotype=pheno[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.phenotypes.extend([ph1, ph2])
        db.session.add(p)
        db.session.commit()

        # Check phenotypes were created
        self.assertEqual(Phenotype.query.count(), 2)

        # Check Particpant has the phenotypes
        for p in Participant.query.first().phenotypes:
            self.assertIn(p.phenotype, pheno)

        # Phenotypes have the participant
        p = Participant.query.first()
        for ph in Phenotype.query.all():
            self.assertEqual(ph.participant_id, p.kf_id)
    
    def test_find_phenotype(self):
        """
        Test find one phenotype
        """
        # Create two phenotypes
        pheno = ['test phenotype 1', 'test phenotype 2']
        ph1 = Phenotype(phenotype=pheno[0])
        ph2 = Phenotype(phenotype=pheno[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.phenotypes.extend([ph1, ph2])
        db.session.add(p)
        db.session.commit()

        # Find phenotype
        ph = Phenotype.query.\
            filter_by(phenotype=pheno[0]).one_or_none()
        self.assertEqual(ph.phenotype, pheno[0])

    def test_update_phenotype(self):
        """
        Test update phenotype
        """
        # Create two phenotypes
        pheno = ['test phenotype 1', 'test phenotype 2']
        ph1 = Phenotype(phenotype=pheno[0])
        ph2 = Phenotype(phenotype=pheno[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.phenotypes.extend([ph1, ph2])
        db.session.add(p)
        db.session.commit()

        # Update and save
        phe = Phenotype.query.filter_by(phenotype=pheno[0]).one_or_none()
        phen = 'test phenotype 3'
        phe.phenotype = phen
        db.session.commit()

        # Check updated values
        phe = Phenotype.query.filter_by(phenotype=phen).one_or_none()
        self.assertIsNot(phe, None)

    def test_delete_phenotype(self):
        """
        Test delete phenotype
        """
        # Create two phenotypes
        pheno = ['test phenotype 1', 'test phenotype 2']
        ph1 = Phenotype(phenotype=pheno[0])
        ph2 = Phenotype(phenotype=pheno[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.phenotypes.extend([ph1, ph2])
        db.session.add(p)
        db.session.commit()

        # Choose one and delete it
        ph = Phenotype.query.filter_by(phenotype=pheno[0]).one_or_none()
        db.session.delete(ph)
        db.session.commit()

        ph = Phenotype.query.filter_by(phenotype=pheno[0]).one_or_none()
        self.assertIs(ph, None)
        phenotypes = [_ph for _ph in p.phenotypes]
        self.assertNotIn(ph, phenotypes)

    def test_delete_phenotype_via_participant(self):
        """
        Test delete related phenotypes via deletion of participant
        """
        # Create two phenotypes
        pheno = ['test phenotype 1', 'test phenotype 2']
        ph1 = Phenotype(phenotype=pheno[0])
        ph2 = Phenotype(phenotype=pheno[1])
        p = Participant(external_id='p1')

        # Add to participant and save
        p.phenotypes.extend([ph1, ph2])
        db.session.add(p)
        db.session.commit()

        # Delete participant
        db.session.delete(p)
        db.session.commit()

        # Check that phenotypes have been deleted
        ph1 = Phenotype.query.filter_by(phenotype=pheno[0]).one_or_none()
        ph2 = Phenotype.query.filter_by(phenotype=pheno[1]).one_or_none()
        self.assertIs(ph1, None)
        self.assertIs(ph2, None)

    def test_not_null_constraint(self):
        """
        Test that a phenotype cannot be created without required
        parameters such as participant_id
        """
        # Create phenotype
        data = {
            'phenotype': 'phenotype_1',
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
            'phenotype': 'phenotype_1',
            'participant_id': ''  # empty blank foreign key
        }
        d = Phenotype(**data)

        # Add to db
        self.assertRaises(IntegrityError, db.session.add(d))

