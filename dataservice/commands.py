# -*- coding: utf-8 -*-
"""Click commands."""

import os

import click

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """ Run the unit tests and pep8 checks """
    from subprocess import call
    call(["python", "-m", "pytest", "tests"])
    call(["python", "-m", "pytest", "--pep8", "dataservice"])


@click.command()
def deploy():
    """ Run deployment tasks """
    from flask.ext.migrate import upgrade

    # migrate database to latest revision
    upgrade()
