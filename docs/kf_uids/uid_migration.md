# Migrating UIDs

Thoughts about UID migration.

## Persist All Old Records

### Translate GET requests

Old style IDs should be replaced with new style IDs, but the old style IDs should become aliases pointing to the new ones.

* Will need a new table in database with two columns: (Old ID, New ID).
  * When adding a new entry to that table, it should see if any existing entries have their New ID equal to the new Old ID. If so, they should be updated to have new New ID. That way all old IDs will always point to the latest ID for the corresponding entity, even if we migrate IDs multiple times.
* GET requests where the requested ID looks like the old style should bounce through the lookup table to get back the corresponding new ID and then return the entity with the new ID in place.

### No need to re-header existing genomic files

Our harmonized genomic files have had biospecimen kfids baked into their bits (not just s3 tags). Updating those would cost extra 💰 beyond just the labor involved. (How much, I don't know. Probably not _thaaaaat_ much.)

We don't need to though. As long as the GET translation is in place, the old KFIDs will continue to be valid.

### Study IDs don't need to change

Changing Study IDs might, especially if we opt for base57 encoding, make S3 bucket formation more annoying. We will just leave studies as they are.
