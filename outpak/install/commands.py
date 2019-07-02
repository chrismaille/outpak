"""Outpak main module."""
import click

from outpak.main.v1 import Outpak


@click.command(help="Install dependencies indicated in pak.yaml")
@click.pass_obj
def install(pak: Outpak) -> None:
    """Install Command.

    :param pak: Outpak instance (click context object)
    :return: None
    """
    pak.run()
