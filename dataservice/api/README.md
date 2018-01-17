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

```
{
  pages: [
    { "doc_id": 30, "value": "Lorem" },
    { "doc_id": 31, "value": "ipsum" },
    { "doc_id": 32, "value": "dolor" },
    ...
    { "doc_id": 40, "value": "amet" }
  ],
  from: 30,
  to: 40,
  results: 10,
  total: 1204,
  message: "Success",
  status: 200
}
```
