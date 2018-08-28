from dataservice.extensions import db
from dataservice.api.genomic_file.models import GenomicFile
from dataservice.api.read_group.models import (
    ReadGroup,
    ReadGroupGenomicFile
)
from tests.utils import IndexdTestCase


class ModelTest(IndexdTestCase):
    """
    Test database model
    """

    def test_create_and_find_read_group(self):
        """
        Test creation of read_group
        """
        self._create_entities()
        self.assertEqual(ReadGroup.query.count(), 2)

        # Check that read group was linked to its gfs
        self.assertEqual(len(ReadGroup.query.filter_by(external_id='rg0')
                             .first().genomic_files), 2)

    def test_update_read_group(self):
        """
        Test updating read_group
        """
        self._create_entities()

        self.assertEqual(ReadGroup.query.count(), 2)
        rg = ReadGroup.query.first()
        rg.flow_cell = 8
        rg.lane_number = 1
        db.session.add(rg)
        db.session.commit()

        rg = ReadGroup.query.get(rg.kf_id)
        self.assertEqual(rg.flow_cell, '8')
        self.assertEqual(rg.lane_number, 1)

    def test_delete_read_group(self):
        """
        Test deleting read_group
        """
        rgs, gfs = self._create_entities()

        self.assertEqual(GenomicFile.query.count(), 2)
        self.assertEqual(ReadGroup.query.count(), 2)
        self.assertEqual(ReadGroupGenomicFile.query.count(), 4)

        # Delete gf linked to 2 read groups
        db.session.delete(gfs[0])
        db.session.commit()
        self.assertEqual(GenomicFile.query.count(), 1)

        # Read groups should all still exist
        self.assertEqual(ReadGroup.query.count(), 2)

        # Only 2 link should remain in link table
        self.assertEqual(ReadGroupGenomicFile.query.count(), 2)
        self.assertEqual(
            ReadGroupGenomicFile.query.filter_by(
                genomic_file_id=gfs[0].kf_id).count(), 0)

    def test_delete_orphans(self):
        """
        Test that orphaned read groups are deleted
        Orphans are read groups with 0 genomic_files
        """
        rgs, gfs = self._create_entities()

        self.assertEqual(ReadGroup.query.count(), 2)

        # Delete all gfs
        for gf in gfs:
            db.session.delete(gf)
        db.session.commit()

        # All read groups should be deleted since they're all orphans
        self.assertEqual(ReadGroup.query.count(), 0)

    def _create_entities(self):
        """
        Make all entities
        """
        # Create many to many rg and gf
        rgs = []
        gfs = []
        for i in range(2):
            gfs.append(
                GenomicFile(external_id='gf{}'.format(i))
            )
            rgs.append(
                ReadGroup(external_id='rg{}'.format(i))
            )

        gfs[0].read_groups.append(rgs[0])
        gfs[0].read_groups.append(rgs[1])
        rgs[0].genomic_files.append(gfs[1])
        rgs[1].genomic_files.append(gfs[1])

        db.session.add_all(rgs + gfs)
        db.session.commit()

        return rgs, gfs
