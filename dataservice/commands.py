# -*- coding: utf-8 -*-
"""Click commands."""

import click


@click.command()
def test():
    """ Run the unit tests and pep8 checks """
    from subprocess import call
    unit = call(["python", "-m", "pytest", "tests"])
    lint = call(["python", "-m", "pytest", "--pep8", "dataservice"])
    exit(max(unit, lint))
