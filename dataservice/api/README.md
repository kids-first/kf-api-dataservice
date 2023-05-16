<center>
![Kids First](/logo)
</center>

Welcome to the developer documentation for the Kids First Dataservice API!

The dataservice is the primary hub for retrieval and creation of Kids First
data. It exposes functionality using a familiar REST interface over HTTP
requests.

# Connect to the API

The API is currently only available internally inside the Kids First cloud
environments.

## curl

Curl is the quickest way to communicate with the api from a unix shell

Get the system status:
```bash
curl -H "Content-Type: application/json" https://kf-api-dataservice.kidsfirstdrc.org/status
```

Create a new study with the name 'my study':
```bash
curl -XPOST -H "Content-Type: application/json" https://kf-api-dataservice.kidsfirstdrc.org/studies -d '{ "name": "my study" }'
```

## Python

We suggest using the popular `requests` package to interact with the API.

To get the system status:
```python
import requests

resp = requests.get('https://kf-api-dataservice.kidsfirstdrc.org/status',
                    headers={'Content-Type': 'application/json'})

print(resp.json())
```

To create a new study:
```python
import requests

body = {
  "name": "my name"
}

resp = requests.post('https://kf-api-dataservice.kidsfirstdrc.org/studies',
                     headers={'Content-Type': 'application/json'},
                     json=body)

print(resp.json())
```

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

### Filter Parameters
The dataservice supports basic filtering of entities via query parameters specified in the query string of the URL.
Entities can be filtered by any of their attributes. The only query operator that is currently supported is `=`.

Additionally, most pagninated resource endpoints also accept the `study_id` query parameter so that
results may be filtered by study. For example:

```
"/participants?after=01-12-2017&study_id=SD_7AWKP3JN&is_proband=true"
```

Will return proband participants created after December 1st, 2017 and which belong to the study identified by the Kids First ID: SD_7AWKP3JN.

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
