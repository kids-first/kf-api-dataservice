kf-api-dataservice
==================

[![license](https://img.shields.io/github/license/kids-first/kf-api-dataservice.svg?style=for-the-badge)](https://github.com/kids-first/kf-api-dataservice/blob/master/LICENSE)
[![CircleCI](https://img.shields.io/circleci/project/kids-first/kf-api-dataservice.svg?style=for-the-badge)](https://circleci.com/gh/kids-first/kf-api-dataservice/13?utm_campaign=vcs-integration-link&utm_medium=referral&utm_source=github-build-link)

The Kids First Data Service provides a REST API to the Kids First data.

## Development

### Developing against the dataservice

If you're developing an application against the dataservice api and the data
it contains, the fastest way to get a development service of your own running
is with docker compose:

```
git clone git@github.com:kids-first/kf-api-dataservice.git
cd kf-api-dataservice
docker-compose up
```

This will start the dataservice api on port `5000` with a backing postgres
database initialized with the current datamodel.

### Developing the dataservice api and model

If you're developing features of the api and the data model behind the
dataservice, you may want finer control over the environment. The following
are the basics to get you started with a local development environment of
your own:

```
# Get source from github
git clone git@github.com:kids-first/kf-api-dataservice.git
cd kf-api-dataservice
# Setup python environment and install dependencies
virtualenv venv &&  source venv/bin/activate
pip install -r dev-requirements.txt
pip install -r requirements.txt
pip install -e .
# Configure the flask application
export FLASK_APP=manage
# Setup the database (using a dockerized postgres)
docker run --name dataservice-pg -p 5432:5432 -d postgres:9.5
docker exec dataservice-pg psql -U postgres -c "CREATE DATABASE dev;"
flask db migrate 
flask db upgrade
# Run the flask web application
flask run 
```

#### Database

Running postgres inside of a container and binding back to the host should
be sufficent for most development needs. If you want to access psql
directly, you can always connect using the following
(assuming the cointainer is named `dataservice-pg` and the database is `dev`):
```
docker exec dataservice-pg psql -U postgres dev
```

If you'd like to use system install of postgres, or a database running remotely,
the dataservice can be configured with the following environment variables:

- `PG_HOST` - the host postgres is running on
- `PG_PORT` - the port postgres is listening on
- `PG_NAME` - the name of the database in postgres
- `PG_USER` - the postgres user to connect with
- `PG_PASS` - the password of the user

## Documentation

The swagger docs are located at the root `localhost:5000/`.

### Generate a Data Model Diagram

An ERD (entity relation diagram) may be found in the `docs/` directory, or may
be produced for changes to the data schema. To do so requires that the latest
development version of
[eralchemy](github.com/Alexis-benoist/eralchemy) be installed:

```
pip install -e git+git@github.com:Alexis-benoist/eralchemy.git#egg=eralchemy
```

This also requires
[GraphViz](https://www.graphviz.org/) be installed as well as
[PyGraphViz](https://pygraphviz.github.io/). PyGraphViz may have trouble finding
GraphViz, in which case, see
[this article](http://www.alexandrejoseph.com/blog/2016-02-10-install-pygraphviz-mac-osx.html).

Once dependencies are installed, run:

```
flask erd
```

A new diagram will be created at `docs/erd.png`.

### Populating Development Database with mock data

to populate database run:

```
flask db_populate
```

to clear the database run:
```
flask clear_db
```

## Testing

Unit tests and pep8 linting is run via `flask test`

```
# Install test dependencies
pip install -r dev-requirements.txt
# Setup test database
docker run --name dataservice-pg -p 5432:5432 -d postgres
docker exec dataservice-pg psql -U postgres -c "CREATE DATABASE test;"
# Run tests
flask test
```

## Deployment

Any commit to any non-master branch that passes tests and contains a
`Jenkinsfile` in the root will be built and deployed to the dev
environment.

Merges to master will be built and deployed to the QA environment
once tests have passed.
