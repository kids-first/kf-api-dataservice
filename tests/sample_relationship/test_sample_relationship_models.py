import pytest

from dataservice.extensions import db
from dataservice.api.sample.models import Sample
from dataservice.api.sample_relationship.models import (
    SampleRelationship,
)
from dataservice.api.errors import DatabaseValidationError
from tests.utils import FlaskTestCase
from tests.sample_relationship.common import create_relationships


class ModelTest(FlaskTestCase):
    """
    Test SampleRelationship database model
    """

    def test_create(self):
        """
        Test create sample relationships
        """
        create_relationships()
        assert 4 == SampleRelationship.query.count()

    def test_parent_child_cannot_be_equal(self):
        """
        Test that if S1 is the parent and S2 is the child then S2 cannot be the
        parent of S1
        """
        create_relationships()

        # Case: create
        sr = SampleRelationship.query.first()
        duplicate = SampleRelationship(
            parent=sr.parent,
            child=sr.parent
        )
        db.session.add(duplicate)
        with pytest.raises(DatabaseValidationError) as e:
            db.session.commit()
        assert "same as" in str(e.value)
        db.session.rollback()
        assert 4 == SampleRelationship.query.count()

        # Case: update
        sr = SampleRelationship.query.first()
        sr.parent = sr.child
        db.session.add(sr)
        with pytest.raises(DatabaseValidationError) as e:
            db.session.commit()
        assert "same as" in str(e.value)

    def test_no_reverse_relation(self):
        """
        Test that if sample S1 is a parent of child S2, then S2 can never be
        the parent of S1
        """
        create_relationships()

        # Case: create
        sr = SampleRelationship.query.first()
        reverse_sr = SampleRelationship(
            parent=sr.child,
            child=sr.parent
        )
        db.session.add(reverse_sr)
        with pytest.raises(DatabaseValidationError) as e:
            db.session.commit()
        assert "Reverse relationship" in str(e.value)
        db.session.rollback()
        assert 4 == SampleRelationship.query.count()

        # Case: update
        rels = SampleRelationship.query.all()
        sr1 = rels[0]
        sr2 = rels[1]
        sr2.parent = sr1.child
        sr2.child = sr1.parent
        db.session.add(sr2)
        with pytest.raises(DatabaseValidationError) as e:
            db.session.commit()
        assert "Reverse relationship" in str(e.value)

    def test_find(self):
        """
        Test find relationship
        """
        _, rels = create_relationships()
        SampleRelationship.query.get(rels[0].kf_id)

    def test_update(self):
        """
        Test update relationship
        """
        _, rels = create_relationships()
        sr = rels[0]
        sr.external_parent_id = "foo"
        sr.external_child_id = "bar"
        db.session.add(sr)
        db.session.commit()
        SampleRelationship.query.filter_by(
            external_parent_id="foo",
            external_child_id="bar",
        ).one()

    def test_delete(self):
        """
        Test deleting a sample relationship
        """
        _, rels = create_relationships()
        sr = rels[0]
        db.session.delete(sr)
        db.session.commit()
        assert 3 == SampleRelationship.query.count()

    def test_delete_via_sample(self):
        """
        Test delete sample relationships via deletion of sample
        """
        _, rels = create_relationships()
        sr = rels[0]
        sa = sr.parent
        db.session.delete(sa)
        db.session.commit()
        assert 3 == SampleRelationship.query.count()

    def test_foreign_key_constraint(self):
        """
        Test that a relationship cannot be created without existing
        reference Sample. This checks foreign key constraint
        """
        # Create sample relationship
        data = {
            "parent_id": "SA_00000000",
            "child_id": "SA_11111111",
            "external_parent_id": "foo",
            "external_child_id": "bar",
        }
        r = SampleRelationship(**data)

        # Add to db
        db.session.add(r)
        with pytest.raises(DatabaseValidationError) as e:
            db.session.commit()
        assert "does not exist" in str(e.value)

    def test_null_parent_allowed(self):
        """
        Test that we can represent a root of a sample tree: a null parent
        with a non-null child
        """
        _, rels = create_relationships()

        pid = rels[0].parent.participant_id
        sample = Sample(
            participant_id=pid, external_id="foo"
        )
        db.session.add(sample)
        db.session.commit()

        # Create sample relationship
        data = {
            "parent_id": None,
            "child_id": sample.kf_id,
            "external_parent_id": None,
            "external_child_id": "foo",
        }
        r = SampleRelationship(**data)

        # Add to db
        db.session.add(r)
        db.session.commit()

        assert len(rels) + 1 == SampleRelationship.query.count()

    def test_null_parent_and_child_not_allowed(self):
        """
        Test that we cannot create a relationship with a null parent and
        child id
        """
        # Create sample relationship
        data = {
            "parent_id": None,
            "child_id": None,
            "external_parent_id": None,
            "external_child_id": None,
        }
        r = SampleRelationship(**data)

        # Add to db
        db.session.add(r)
        with pytest.raises(DatabaseValidationError) as e:
            db.session.commit()
        assert "cannot be null" in str(e.value)

    def test_query_all_relationships(self):
        """
        Test the class method query_all_relationships on SampleRelationship

        Given a sample"s kf_id, this method should return all of the
        immediate/direct sample relationships of the sample.
        """
        studies, rels = create_relationships()
        study_id = studies[0]

        # Query all samples
        assert 4 == SampleRelationship.query_all_relationships().count()

        # Query by sample

        # First add more children in the sample tree
        sr = rels[0]
        pid = sr.parent.participant_id
        s3 = Sample(
            external_id="SA-003", sample_type="Saliva",
            participant_id=pid
        )
        s4 = Sample(
            external_id="SA-004", sample_type="Blood",
            participant_id=pid
        )
        sr1 = SampleRelationship(parent=sr.parent, child=s3)
        sr2 = SampleRelationship(parent=sr.parent, child=s4)
        db.session.add_all([sr1, sr2])
        db.session.commit()

        assert 3 == SampleRelationship.query_all_relationships(
            sr.parent.kf_id
        ).count()
