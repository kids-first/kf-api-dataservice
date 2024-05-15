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
    __table_args__ = (db.UniqueConstraint('parent_id', 'child_id',),)

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    parent_id = db.Column(
        KfId(),
        db.ForeignKey('sample.kf_id'),
        nullable=False,
        doc='kf_id of one sample in the relationship')

    child_id = db.Column(
        KfId(),
        db.ForeignKey('sample.kf_id'),
        nullable=False,
        doc='kf_id of the other sample in the relationship')

    external_parent_id = db.Column(db.Text())

    external_child_id = db.Column(db.Text())

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
        """
        # Apply model property filter params
        if model_filter_params is None:
            model_filter_params = {}
        q = SampleRelationship.query.filter_by(**model_filter_params)

        # # Get sample relationships and join with sample
        # q = q.join(Sample, or_(SampleRelationship.parent,
        #                        SampleRelationship.child))

        # Do this bc query.get() errors out if passed None
        if sample_kf_id:
            sa = Sample.query.get(sample_kf_id)
            q = q.filter(or_(
                SampleRelationship.parent_id == sample_kf_id,
                SampleRelationship.child_id == sample_kf_id))

        # Don't want duplicates - return unique family relationships
        q = q.group_by(SampleRelationship.kf_id)

        return q

    def __repr__(self):
        return f"{self.parent.kf_id} parent of {self.child.kf_id}"
