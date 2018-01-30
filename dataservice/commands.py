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


@click.command()
def erd():
    """ Create an ERD of the current data model """
    import os
    from eralchemy import render_er
    from dataservice.api.participant.models import Participant

    if not os.path.isdir('docs'):
        os.mkdir('docs')

    render_er(Participant, os.path.join('docs', 'erd.png'))
