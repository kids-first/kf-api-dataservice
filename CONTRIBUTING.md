# 👥 Contributing to the Kids First Dataservice API

## Adding fields

Over time, new data comes into the Kids First ecosystem, requiring the
Dataservice to adapt. In these cases, developers need to add new columns or
change columns in the Dataservice DB and API.

### Where to Add Fields

In order to add a new field to the Dataservice, the developer needs to know
which table to add the field to. All entity types in the Dataservice have a
standard folder structure like this:

```rtf
dataservice/api/genomic_file
|-- README.md
|-- __init__.py
|-- models.py
|-- resources.py
`-- schemas.py
```

`models.py` is where the table schema is defined, using the SQLAlchemy ORM
(object relational mapper). To understand how the SQLAlchemy model object and
database table are related you can read more about the SQLAlchemy ORM.

There are 2 things you need to modify in this file.

1. Please add a parameter and type description for the new field in the
   class's docstring
2. Add the field using SQLAlchemy's Column object. Take a look at other fields
   as an example.

Column data types can be found in [SQLAlchemy documentation](https://docs.sqlalchemy.org/en/20/core/type_basics.html#generic-camelcase-types),
but the most common data types used in the dataservice are `Text`, `Boolean`,
`Integer`, `Float`, and `DateTime`.

### Example

As an example, take adding a new field, `my_new_field` to the `genomic_file`
endpoint. This is a free text field.

In the file `dataservice/api/genomic_file/models.py`, add the docstring for
the new field:

```python
    :param new_field_name: Description of the new field.
```

Then a new object is added for this new field:

```python
    new_field_name = db.Column(
        db.Text(),
        doc = 'Description of the new field'
    )
```

### Database Migration

Now that you've added the new column to the entity's model class, you will
need to generate a database migration script which when run will actually
modify the database and it's schema to add the new column.

This step must be completed for every newly added field.

From the root of the repository, run:

To create the migration:

```sh
flask db migrate -m "name of migration"
```

Then, to apply the migration:

```sh
flask db upgrade
```

Last, add the semantic version number to the docstring of the generated
migration file.

### Testing

After adding the new field to the model, tests need to be added so that the new
field can be tested to see if it works as intended. There are a few key places
where testing needs to be added/ modified:

1. `tests/data.json` - valid data

    This file holds data used in some testing steps. The newly added field and
    valid fake data need to be added to this document. The new field should be
    added under the related endpoint's object. So, taking the above discussed
    new field, `new_field_name` field in the `genomic_file` endpoint, this new
    field would be added under `/genomic-files` with a json name/value pair:

    ```json
    {
        ...
        "/genomic-files": {
            "external_id": "GenomicFile_0",
            ...
            "new_field_name": "some value",
            ...
            "visible": true
        }
        ...
    }
    ```

2. `tests/data.json` - invalid data

    If the new field has enumerated values or is not a text field, also add
    valid and invalid data to `data.json`. These data are added within the
    `filter_params` object. A set of valid field name/value pairs are provided
    in an object and a set of invalid field name/value pairs are provided in an
    array:

    ```json
    {
        ...
        "filter_params": {
            ...
            "/genomic-files": {
                "valid": {
                    "external_id": "GenomicFile_1",
                    ...
                    "new_field_name": "some valid value"
                },
                "invalid": [
                    { "paired_end": -1 },
                    ...
                    { "new_field_name": "some invalid value" }
                ]
            }
            ...
        }
    }
    ```

3. `tests/create/py` __biospecimens only__

    For biospecimens only, add the new field with a valid value to the body
    object in the function `make_biospecimen`.

4. `tests/[endpoint_name]/test_[endpoint_name]_models.py`

    Testing has changed over time so the format of this file depends on the how
    testing was performed when the testing script was written. In this file,
    look for a place where a dictionary object is created with key/value pairs
    for all of the endpoint's fields and add a new, relevant key/value pair for
    the new field.

5. `tests/[endpoint_name]/test_[endpoint_name]_resources.py`

    Testing has changed over time so the format of this file depends on the how
    testing was performed when the testing script was written. In this file,
    look for a place where a dictionary object is created with key/value pairs
    for all of the endpoint's fields and add a new, relevant key/value pair for
    the new field.

## Pull Requests

After making changes, make sure to format your commit messages using the
guidance provided by the
[KF Developer Handbook](https://kids-first.github.io/kf-developer-handbook/guides/commit_messages.html).
Then, push your changes and make a pull request (again following those
guidelines). Make sure that all of the linting and tests pass and then request
a review on the PR by @dataservice-reviewers. Once approved, merge the PR and
delete the feature branch.

## Releases

After merging a PR into the master branch of the dataservice Github repository,
Jenkins picks up the change and rebuilds the Dataservice docker image. This
image is then deployed into the QA environment.

To release to production, follow the instructions provided by the [d3b-release-maker](https://github.com/d3b-center/d3b-release-maker/)
to install and use the release maker. This tool will create a release PR.
Request review by @dataservice-reviewers. Once the pull request is approved,
merge it. Jenkins will then pick up the change and build the dataservice in
production.
