"""Click Command main module."""
import click
import importlib as importlib

from outpak.config import load_from_yaml
from outpak.install.commands import install
from outpak.release.commands import release


@click.group()
@click.option('--config', envvar='OUTPAK_FILE', required=True, type=click.Path())
@click.pass_context
def cli(ctx, config) -> None:
    """Click main group command."""
    data = load_from_yaml(config)
    klass = importlib.import_module(f"outpak.main.v{data['version']}.Outpak")
    obj = klass(config, data)  # type: ignore
    obj.validate_data()
    ctx.obj = obj


cli.add_command(install)
cli.add_command(release)


def start() -> None:
    """Start command.

    :return: None
    """
    cli()
