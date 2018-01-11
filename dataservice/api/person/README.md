A person is one of the central entities of the Kid's First DCC.

### Fields

`kf_id` - the unique identifier assigned by Kid's First used as the primary
reference to this Person

`source_name` - the identifier used by the original contributor of the data

`date_created` - the date the person`s record was created in the DCC

`date_modified` - the last date that the record's fields were modified.
Restricted to fields of the entity itself, not any of it's related entities.

### Identifiers

The Kid's First DCC assigns a unique, internal identifier of the form:
`KF-P000000` on creation of a new Person. This identifier is used accross the
Kids First Data Service and Data Resource Portal It is expected that the Person
also have an identifier unique to the study it came from. This field is to be
captured in the `source_name` property of the Person upon creation.
