"""Outpak.

Usage:
  pak install [--config=<path>]
  pak -h | --help
  pak --version

Options:
  -h --help         Show this screen.
  --version         Show version.
  --config=<path>  Full path for pak.yml
"""
import os
from docopt import docopt
from outpak import __version__
from buzio import console
from outpak.main import Outpak


def get_path():
    """Get pak.yml full path.

    Returns
    -------
        Str: full path from current path

    """
    return os.path.join(
        os.getcwd(),
        'pak.yml'
    )


def get_from_env():
    """Get OUTPAK_FILE value.

    Returns
    -------
        Str: value from memory

    """
    return os.getenv('OUTPAK_FILE')


def run():
    """Run main command for outpak."""
    console.box("Outpak v{}".format(__version__))
    arguments = docopt(__doc__, version=__version__)

    path = None
    if arguments['--config']:
        path = arguments['--config']

    if not path:
        path = get_from_env()

    if not path:
        path = get_path()

    if arguments['install']:
        newpak = Outpak(path)
        newpak.run()


if __name__ == "__main__":
    run()
