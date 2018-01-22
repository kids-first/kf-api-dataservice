Primary API for interacting with the Kid's First Data Model.

## Service-Wide Standards and Functionality

### Field Masking

Partial data fetching is supported via the `X-Fields` header.
To specifiy that only some fields are to be returned, include a bracketed,
coma-delimited list under the `X-Fields` header:

`X-Fields: {kf_id, name}`

Brackets may be nested to filter on nested fields:

`X-Fields: {kf_id, name, type{format, extension}}`

An asterisk may be used to specify all fields:

`X-Fields: *`

Or all sub-fields:

`X-Fields: {kf_id, type{*}}`

Or all root fields, but with only some sub-fields:

`X-Fields: {*, type{format}}`



### Pagination

Most resource containers are paginated and return 10 entries by default.
Links to the next and previous page are provided in the `_links`.

```
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
