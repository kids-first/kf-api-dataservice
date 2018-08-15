import uuid

from dataservice.extensions import db
from dataservice.api.study.models import Study
from dataservice.api.participant.models import Participant
from dataservice.api.biospecimen.models import Biospecimen
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.sequencing_center.models import SequencingCenter
from dataservice.api.read_group.models import ReadGroup
from tests.utils import IndexdTestCase


class ModelTest(IndexdTestCase):
    """
    Test database model
    """

    def test_create_and_find_read_group(self):
        """
        Test creation of read_group
        """
        self._create_read_group()
        self.assertEqual(ReadGroup.query.count(), 1)
        self.assertEqual(len(ReadGroup.query.first().genomic_files), 3)

    def test_update_read_group(self):
        """
        Test updating read_group
        """
        self._create_read_group()

        self.assertEqual(ReadGroup.query.count(), 1)
        rg = ReadGroup.query.first()
        rg.flow_cell = 8
        rg.lane_number = 1
        db.session.add(rg)
        db.session.commit()

        rg = ReadGroup.query.first()
        self.assertEqual(rg.flow_cell, '8')
        self.assertEqual(rg.lane_number, 1)

    def test_delete_read_group(self):
        """
        Test deleting read_group
        """
        self._create_read_group()
        self.assertEqual(ReadGroup.query.count(), 1)
        rg = ReadGroup.query.first()

        # Delete read group
        db.session.delete(rg)
        db.session.commit()

        # Both read group and child genomic files should be deleted
        self.assertEqual(ReadGroup.query.count(), 0)
        self.assertEqual(GenomicFile.query.count(), 0)

    def test_delete_orphans(self):
        """
        Test that orphaned read groups are deleted
        Orphans are read groups with 0 genomic_files
        """
        kwargs = self._create_read_group()
        kf_id = kwargs.get('kf_id')

        rg2 = ReadGroup()
        gf = GenomicFile()
        rg2.genomic_files.append(gf)
        db.session.add(rg2)
        db.session.commit()

        # Delete genomic files from read group
        for gf in ReadGroup.query.get(kf_id).genomic_files:
            db.session.delete(gf)
        db.session.commit()

        # Check that orphan was deleted and other read_group was unaffected
        self.assertEqual(1, ReadGroup.query.count())
        self.assertIsNone(ReadGroup.query.get(kf_id))
        self.assertEqual(rg2, ReadGroup.query.first())

    def _create_read_group(self):
        """
        Create read group
        """
        self._create_entities()
        gfs = GenomicFile.query.all()
        kwargs = {
            "external_id": "FL01",
            "flow_cell": "FL123",
            "lane_number": 4,
            "quality_scale": "Illumina15"
        }
        rg = ReadGroup(**kwargs)
        for gf in gfs:
            gf.read_group = rg

        db.session.add(rg)
        db.session.commit()

        kwargs['kf_id'] = rg.kf_id

        return kwargs

    def _create_entities(self):
        """
        Make all entities up to genomic_file
        """
        # Create study
        study = Study(external_id='phs001')

        # Create participant
        p = Participant(external_id='p1', is_proband=True, study=study)

        # Create sequencing_center
        sc = SequencingCenter.query.filter_by(name="Baylor").one_or_none()
        if sc is None:
            sc = SequencingCenter(name="Baylor")
            db.session.add(sc)
            db.session.commit()

        # Create biospecimen
        bs = Biospecimen(external_sample_id='bio1',
                         analyte_type='dna',
                         participant_id=p.kf_id,
                         sequencing_center_id=sc.kf_id)

        # Create genomic files
        for i in range(3):
            kwargs = {
                'file_name': 'fastq-{}'.format(i),
                'data_type': 'Unaligned Reads',
                'file_format': '.fq',
                'urls': ['s3://seq-data/reads.fq'],
                'hashes': {'md5': str(uuid.uuid4())},
                'paired_end': 1,
                'controlled_access': True,
                'is_harmonized': False,
                'reference_genome': None
            }
            gf = GenomicFile(**kwargs)
            bs.genomic_files.append(gf)

        p.biospecimens = [bs]
        db.session.add(p)
        db.session.commit()
