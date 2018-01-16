# -*- coding: utf-8 -*-
"""Click commands."""

import click


@click.command()
def test():
    """ Run the unit tests and pep8 checks """
    from subprocess import call
    call(["python", "-m", "pytest", "tests"])
    call(["python", "-m", "pytest", "--pep8", "dataservice"])
