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
The dataservice uses the timestamp of the time of the object's creation
to paginate. Specific dates may also be used. For example:

```
"/participants?after=01-12-2017",
```
Will list all participants created after December 1st, 2017.


An example of the envelope wrapping a paginated response:
```json
{
    "_links": {
        "next": "/participants?after=1519220889.046443",
        "self": "/participants?after=1519220889.035079"
    },
    "_status": {
        "code": 200,
        "message": "success"
    },
    "limit": 10,
    "results": [
      ...
    ],
    "total": 50
}
```
