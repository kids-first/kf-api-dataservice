
from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.sample.models import Sample
from dataservice.api.sample_relationship.models import (
    SampleRelationship,
)


def create_relationships():
    """
    Create sample relationships and required entities
    """
    # 2 studies, 2 participants per study, 2 samples per participant,
    # 1 sample relationship per participant/study
    studies = []
    sample_relationships = []
    for i in range(2):
        studies.append(Study(external_id=f"study_{i}"))

    for i in range(4):
        p = Participant(external_id=f"P{i}", is_proband=False)
        samples = [Sample(external_id=f"SA{i}-{j}") for j in range(2)]
        sr = SampleRelationship(
            parent=samples[0],
            external_parent_id=samples[0].external_id,
            child=samples[1],
            external_child_id=samples[1].external_id,
        )
        sample_relationships.append(sr)
        p.samples.extend(samples)
        if i % 2 == 0:
            studies[0].participants.append(p)
        else:
            studies[1].participants.append(p)

    db.session.add_all(studies)
    db.session.commit()

    return studies, sample_relationships
