# -*- coding: utf-8 -*-

import logging
import time
import click

import ckan.model as model
import ckanext.syndicate.utils as utils


def get_commands():
    return [syndicate]


@click.group()
def syndicate():
    pass


@syndicate.command()
def seed():
    """Fill database with syndication profiles."""
    utils.seed_db()


@syndicate.command()
@click.argument("id", required=False)
@click.option("-t", "--timeout", type=float, default=0)
@click.option("-v", "--verbose", count=True)
def sync(id, timeout, verbose):
    """Syndicate datasets to remote portals."""

    packages = model.Session.query(model.Package)
    if id:
        packages = packages.filter(
            (model.Package.id == id) | (model.Package.name == id)
        )

    total = packages.count()

    if not verbose:
        logging.getLogger("ckanext.syndicate.plugin").propagate = False
        logging.getLogger("ckan.lib.jobs").propagate = False

    with click.progressbar(packages, length=total) as bar:
        for package in bar:
            bar.label = "Sending syndication signal to package {}".format(
                package.id
            )
            utils.try_sync(package.id)
            time.sleep(timeout)


@syndicate.command()
def init():
    """Creates new syndication table."""
    utils.reset_db()
    click.secho("DB tables are reinitialized", fg="green")
