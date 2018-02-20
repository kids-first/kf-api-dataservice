Primary API for interacting with the Kid's First Data Model.

# Identifiers

The Kids First dataservice assigns an id to each entity stored in it's
internal model upon entry into the service. This id, or `kf_id`, is the primary
means of retrieving and referencing data in the Kids First ecosystem. The
format of the `kf_id` is an 8 character,
[Crockford](http://www.crockford.com/wrmg/base32.html)
encoded string prefix with a two character prefix denoting the entity type
and seperated by an underscore.
Some examples:

 - `PH_CZHXGVPB` - A Phenotype
 - `SA_SN4GWD2Q` - A Sample
 - `PT_1AWEK8QD` - A Participant
 - `OC_SBP09501` - An Outcome

# Pagination

Most resource containers are paginated and return 10 entries by default.
Links to the next and previous page are provided in the `_links`.

```json
{
  "_links": {
    "next": "/participants?page=3",
    "self": "/participants?page=2",
    "prev": "/participants?page=1"
  },
  "_status": {
    "code": 200,
    "message": "OK"
  }
  "total": 1204,
  "limit": 10,
  "results": [
    { "doc_id": 30, "value": "Lorem" },
    { "doc_id": 31, "value": "ipsum" },
    { "doc_id": 32, "value": "dolor" },
    ...
    { "doc_id": 40, "value": "amet" }
  ],
}
```
