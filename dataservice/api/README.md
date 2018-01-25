Primary API for interacting with the Kid's First Data Model.

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
