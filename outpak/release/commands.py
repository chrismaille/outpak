"""Release command code."""
import click

from outpak.main.v1 import Outpak


@click.group(help="Create, update or delete releases")
@click.pass_context
def release(ctx) -> None:
    """Click release group.

    :param ctx: Click context
    :return: None
    """
    pass


@release.command(help="Create new release")
@click.option('--pre', is_flag=True)
@click.pass_obj
def create(pak: Outpak, pre: bool) -> None:
    """Release Create command.

    :param pak: Outpak instance (Click context object)
    :param pre: boolean - its a pre-release?
    :return: None
    """
    pass
