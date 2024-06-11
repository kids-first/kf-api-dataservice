from sqlalchemy import event, or_


from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.sample.models import Sample


class SampleRelationship(db.Model, Base):
    """
    Represents a relationship between two samples.

    The relationship table represents a tree.

    :param kf_id: Primary key given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param parent_id: Kids first id of the parent Sample in the
    relationship
    :param child_id: Kids first id of the child Sample
    in the relationship
    :param external_parent_id: Name given to parent sample by contributor
    :param external_child_id: Name given to child sample by contributor
    :param notes: Text notes from source describing the sample relationship
    """
    __tablename__ = 'sample_relationship'
    __prefix__ = 'SR'
    __table_args__ = (db.UniqueConstraint('child_id',),)

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    parent_id = db.Column(
        KfId(),
        db.ForeignKey('sample.kf_id'),
        nullable=True,
        doc='kf_id of one sample in the relationship')

    child_id = db.Column(
        KfId(),
        db.ForeignKey('sample.kf_id'),
        nullable=True,
        doc='kf_id of the other sample in the relationship')

    external_parent_id = db.Column(
        db.Text(),
        doc='Name given to parent sample by contributor'
    )
    external_child_id = db.Column(
        db.Text(),
        doc='Name given to child sample by contributor'
    )

    notes = db.Column(
        db.Text(),
        doc='Text notes describing the relationship'
    )

    parent = db.relationship(
        Sample,
        primaryjoin=parent_id == Sample.kf_id,
        backref=db.backref('outgoing_sample_relationships',
                           cascade='all, delete-orphan'))

    child = db.relationship(
        Sample,
        primaryjoin=child_id == Sample.kf_id,
        backref=db.backref('incoming_sample_relationships',
                           cascade='all, delete-orphan'))

    @classmethod
    def query_all_relationships(cls, sample_kf_id=None,
                                model_filter_params=None):
        """
        Find all sample relationships for a sample

        :param sample_kf_id: Kids First ID of the sample
        :param model_filter_params: Filter parameters to the query

        Given a sample's kf_id, return all of the immediate/direct sample
        relationships of the sample.

        We cannot return a all samples in the tree bc this would require
        a recursive query which Dataservice would likely need to do in a
        longer-running task. The service is not setup for this
        """
        # Apply model property filter params
        if model_filter_params is None:
            model_filter_params = {}
        q = SampleRelationship.query.filter_by(**model_filter_params)

        # Get sample relationships and join with sample
        q = q.join(Sample, or_(SampleRelationship.parent,
                               SampleRelationship.child))

        # Do this bc query.get() errors out if passed None
        if sample_kf_id:
            sa = Sample.query.get(sample_kf_id)
            q = q.filter(or_(
                SampleRelationship.parent_id == sample_kf_id,
                SampleRelationship.child_id == sample_kf_id))

        # Don't want duplicates - return unique sample relationships
        q = q.group_by(SampleRelationship.kf_id)

        return q

    def __repr__(self):
        return f"{self.parent.kf_id} parent of {self.child.kf_id}"


def validate_sample_relationship(target):
    """
    Ensure that the reverse relationship does not already exist
    Ensure that the parent != child

    If these are not the case then raise DatabaseValidationError

    :param target: the sample_relationship being validated
    :type target: SampleRelationship
    """
    from dataservice.api.errors import DatabaseValidationError

    # Return if sample_relationship is None
    if not target:
        return

    parent_id = target.parent_id
    child_id = target.child_id

    # Check that at least 1 sample ID is non-null
    if not (parent_id or child_id):
        raise DatabaseValidationError(
            SampleRelationship.__tablename__,
            "modify",
            "Both parent_id and child_id cannot be null"
        )

    # If a parent_id or child_id is not-null then check that the ID
    # refers to an existing sample
    for sample_id in [parent_id, child_id]:
        if sample_id:
            sample = Sample.query.get(sample_id)
            if not sample:
                raise DatabaseValidationError(
                    SampleRelationship.__tablename__,
                    "modify",
                    f"Either parent sample {target.parent_id} or "
                    f"child sample {target.child_id} or both does not exist"
                )

    # Check for reverse relation
    sr = SampleRelationship.query.filter_by(
        parent_id=child_id,
        child_id=parent_id,
    ).first()

    if sr:
        raise DatabaseValidationError(
            SampleRelationship.__tablename__,
            "modify",
            f"Reverse relationship, Parent: {parent_id} -> Child: "
            f"{child_id}, not allowed since the SampleRelationship, "
            f"Parent: {sr.parent_id} -> Child: {sr.child_id}, already exists"
        )

    # Check for parent = child
    if parent_id == child_id:
        raise DatabaseValidationError(
            SampleRelationship.__tablename__,
            "modify",
            f"Cannot create Sample relationship where parent sample is the"
            " same as the child sample"
        )


@event.listens_for(SampleRelationship, 'before_insert')
@event.listens_for(SampleRelationship, 'before_update')
def relationship_on_insert_or_update(mapper, connection, target):
    """
    Run preprocessing/validation of relationship before insert or update
    """
    validate_sample_relationship(target)
