import json
import uuid
from flask import url_for

from dataservice.extensions import db
from dataservice.utils import iterate_pairwise
from dataservice.api.study.models import Study
from dataservice.api.investigator.models import Investigator
from dataservice.api.study_file.models import StudyFile
from dataservice.api.participant.models import Participant
from dataservice.api.family.models import Family
from dataservice.api.family_relationship.models import FamilyRelationship
from dataservice.api.diagnosis.models import Diagnosis
from dataservice.api.outcome.models import Outcome
from dataservice.api.phenotype.models import Phenotype
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.cavatica_task.models import (
    CavaticaTask,
    CavaticaTaskGenomicFile
)
from tests.utils import IndexdTestCase
from tests.conftest import ENTITY_ENDPOINT_MAP

STUDY_URL = 'api.studies'
STUDY_LIST_URL = 'api.studies_list'


class StudyTest(IndexdTestCase):
    """
    Test study api endopoints
    """

    def test_post_study(self):
        """
        Test creating a new study
        """
        response = self._make_study(external_id='TEST')
        resp = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)

        self.assertIn('study', resp['_status']['message'])
        self.assertIn('created', resp['_status']['message'])
        self.assertNotIn('_id', resp['results'])

        s = Study.query.first()
        study = resp['results']
        self.assertEqual(s.kf_id, study['kf_id'])
        self.assertEqual(s.external_id, study['external_id'])

    def test_get_study(self):
        """
        Test retrieving a study by id
        """
        resp = self._make_study('TEST')
        resp = json.loads(resp.data.decode('utf-8'))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(STUDY_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        study = resp['results']
        self.assertEqual(kf_id, study['kf_id'])

    def test_get_study_no_investigator(self):
        """
        Test that the investigator link is set to null
        if the study doesnt have an investigator
        """
        resp = self._make_study(include_nullables=False)
        resp = json.loads(resp.data.decode("utf-8"))
        kf_id = resp['results']['kf_id']

        response = self.client.get(url_for(STUDY_URL,
                                           kf_id=kf_id),
                                   headers=self._api_headers())
        resp = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)

        self.assertTrue('investigator' in resp['_links'])
        self.assertIs(None, resp['_links']['investigator'])

    def test_patch_study(self):
        """
        Test updating an existing study
        """
        response = self._make_study(external_id='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        study = resp['results']
        kf_id = study.get('kf_id')
        external_id = study.get('external_id')

        # Update the study via http api
        body = {
            'external_id': 'new_id',
            'release_status': 'Pending'
        }
        response = self.client.patch(url_for(STUDY_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Study.query.get(kf_id).external_id,
                         body['external_id'])

        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('study', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        study = resp['results']
        self.assertEqual(study['kf_id'], kf_id)
        self.assertEqual(study['external_id'], body['external_id'])
        self.assertEqual(study['release_status'], body['release_status'])

    def test_patch_study_no_required_field(self):
        """
        Test that we may update the study without a required field
        """
        response = self._make_study(external_id='TEST')
        resp = json.loads(response.data.decode('utf-8'))
        study = resp['results']
        kf_id = study.get('kf_id')
        external_id = study.get('external_id')

        # Update the study via http api
        body = {
            'version': '2.0'
        }
        response = self.client.patch(url_for(STUDY_URL,
                                             kf_id=kf_id),
                                     headers=self._api_headers(),
                                     data=json.dumps(body))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Study.query.get(kf_id).version, '2.0')

        resp = json.loads(response.data.decode('utf-8'))
        self.assertIn('study', resp['_status']['message'])
        self.assertIn('updated', resp['_status']['message'])

        study = resp['results']
        self.assertEqual(study['kf_id'], kf_id)
        self.assertEqual(study['external_id'], external_id)
        self.assertEqual(study['version'], body['version'])

    def test_delete_cascade_study(self):
        """
        Test deleting a study by id
        """
        self._create_full_study('s0', 2)
        self._create_full_study('s1', 4)
        s0 = Study.query.filter_by(external_id='s0').one()
        response = self.client.delete(url_for(STUDY_URL,
                                              kf_id=s0.kf_id),
                                      headers=self._api_headers())
        assert response.status_code == 200

        # Check counts
        assert 1 == Study.query.count()
        assert 4 == StudyFile.query.count()
        assert 1 == Family.query.count()
        assert 4 == Participant.query.count()
        assert 4 == Outcome.query.count()
        assert 4 == Diagnosis.query.count()
        assert 4 == Phenotype.query.count()
        assert 4 == Biospecimen.query.count()
        assert 16 == GenomicFile.query.count()
        assert 3 == FamilyRelationship.query.count()
        assert 16 == CavaticaTaskGenomicFile.query.count()

        # Check content
        model_classes = ENTITY_ENDPOINT_MAP.keys()
        skip = {'SequencingCenter', 'CavaticaTask', 'CavaticaTaskGenomicFile'}
        for model_cls in model_classes:
            for obj in model_cls.query.all():
                if model_cls.__name__ == 'Biospecimen':
                    attr = 'external_sample_id'
                else:
                    attr = 'external_id'
                # All s0 objects should not exist
                if model_cls.__name__ in skip:
                    continue
                assert getattr(obj, attr).startswith('s0') == False

    def _make_study(self, external_id='TEST-0001', include_nullables=True):
        """
        Convenience method to create a study with a given source name
        """
        inv = Investigator(name='donald duck')
        db.session.add(inv)
        db.session.flush()

        body = {
            'external_id': external_id,
            'version': '1.0',
            'release_status': 'Pending'
        }
        if include_nullables:
            body.update({'investigator_id': inv.kf_id})

        response = self.client.post(url_for(STUDY_LIST_URL),
                                    headers=self._api_headers(),
                                    data=json.dumps(body))
        return response

    def _create_full_study(self, study_ext_id=0, n_participants=1):
        # Sequencing center
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()

        # Create study
        s0 = Study(external_id='{}'.format(study_ext_id))
        f0 = Family(external_id='{}'.format(study_ext_id))
        participants = []
        for i in range(n_participants):
            data = {
                'file_name': '{}_sf{}.csv'.format(study_ext_id, i),
                'external_id': '{}_sf{}.csv'.format(study_ext_id, i),
                'data_type': 'clinical',
                'file_format': 'csv',
                'availability': 'Immediate Download',
                'size': 1024,
                'urls': ['s3://mystudy/my_data.csv'],
                'hashes': {
                    'md5': str(uuid.uuid4()).replace('-', '')
                }
            }
            sf = StudyFile(**data)
            p = Participant(external_id='{}_p{}'.format(study_ext_id, i),
                            is_proband=True,
                            study=s0, family=f0)
            Diagnosis(external_id='{}_d{}'.format(study_ext_id, i),
                      participant=p)
            Phenotype(external_id='{}_ph{}'.format(study_ext_id, i),
                      participant=p)
            Outcome(external_id='{}_ot{}'.format(study_ext_id, i),
                    participant=p)
            # Biospecimen
            bs = Biospecimen(external_sample_id='{}_bs{}'.format(study_ext_id,
                                                                 i),
                             analyte_type='dna',
                             sequencing_center=sc,
                             participant=p)
            # SequencingExperiment
            data = {
                'external_id': '{}_se{}'.format(study_ext_id, i),
                'experiment_strategy': 'wgs',
                'is_paired_end': True,
                'platform': 'platform',
                'sequencing_center': sc
            }
            se = SequencingExperiment(**data)
            data = {
                'external_cavatica_task_id': str(uuid.uuid4()),
                'name': '{}_ct{}'.format(study_ext_id, i),
            }
            ct = CavaticaTask(**data)
            # Genomic Files
            for i in range(4):
                data = {
                    'file_name': '{}_gf_{}.bam'.format(study_ext_id, i),
                    'external_id': '{}_gf_{}'.format(study_ext_id, i),
                    'data_type': 'submitted aligned read',
                    'file_format': '.cram',
                    'urls': ['s3://file_{}'.format(i)],
                    'hashes': {'md5': str(uuid.uuid4())},
                    'is_harmonized': True if i % 2 else False,
                    'sequencing_experiment': se,
                    'biospecimen': bs
                }
                gf = GenomicFile(**data)
                CavaticaTaskGenomicFile(cavatica_task=ct, genomic_file=gf,
                                        is_input=True)

            sf.study = s0
            p.study = s0
            p.family = f0
            participants.append(p)

        db.session.add(s0)
        db.session.commit()

        # Create family_relationships
        self._create_family_rels(study_ext_id, participants)

    def _create_family_rels(self, study_ext_id, participants):
        # Family relationships
        for i, (participant, relative) in enumerate(iterate_pairwise(
                participants)):
            gender = participant.gender
            rel = 'mother'
            if gender == 'male':
                rel = 'father'
            r = FamilyRelationship(external_id='{}_fr_{}'.format(study_ext_id,
                                                                 i),
                                   participant=participant,
                                   relative=relative,
                                   participant_to_relative_relation=rel)
            db.session.add(r)
        db.session.commit()
