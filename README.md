kf-api-dataservice
==================

[![license](https://img.shields.io/github/license/kids-first/kf-api-dataservice.svg?style=for-the-badge)](https://github.com/kids-first/kf-api-dataservice/blob/master/LICENSE)
[![CircleCI](https://img.shields.io/circleci/project/kids-first/kf-api-dataservice.svg?style=for-the-badge)](https://circleci.com/gh/kids-first/kf-api-dataservice/13?utm_campaign=vcs-integration-link&utm_medium=referral&utm_source=github-build-link)

The Kids First Data Service provides a REST API to the Kids First data.

## Development

Start a development service of your own:

```
# Get source from github
git clone git@github.com:kids-first/kf-api-dataservice.git
cd kf-api-dataservice
# Setup python environment and install dependencies
virtualenv venv &&  source venv/bin/activate
pip install -r dev-requirements.txt
pip install -r requirements.txt
# Configure the flask application
export FLASK_APP=manage
# Setup the database
docker run --name dataservice-pg -p 5432:5432 -d postgres:9.5
docker exec dataservice-pg psql -U postgres -c "CREATE DATABASE dev;"
flask db upgrade
# Run the flask web application
flask run 
```

### Database

The example environment above uses docker to run a Postgres instance,
however, a local install of Postgres may be used just as easily.

The API should now be available at `localhost:5000/`.

## Documentation

The swagger docs are located at the root `localhost:5000/`.

### Generate a Data Model Diagram

An ERD (entity relation diagram) may be found in the `docs/` directory, or may
be produced for changes to the data schema. To do so requires that 
[GraphViz](https://www.graphviz.org/) be installed as well as
[PyGraphViz](https://pygraphviz.github.io/). PyGraphViz may have trouble finding
GraphViz, in which case, see
[this article](http://www.alexandrejoseph.com/blog/2016-02-10-install-pygraphviz-mac-osx.html).

Once dependencies are installed, run:

```
flask erd
```

A new diagram will be created at `docs/erd.png`.


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
