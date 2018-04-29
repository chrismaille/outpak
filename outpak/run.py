"""Outpak.

Usage:
  pak install [--config=<path>] [--quiet]
  pak -h | --help
  pak --version

Options:
  -h --help         Show this screen.
  --quiet           Run pip with -q option (silent mode)
  --version         Show version.
  --config=<path>  Full path for pak.yml
"""
import os
from docopt import docopt
from outpak import __version__
from buzio import console

from outpak.config import OutpakConfig
from outpak.command import OutpakCommand


def get_path(arguments):
    """Get pak.yml full path.

    Returns
    -------
        Str: full path from current path

    """
    if arguments['--config']:
        return arguments['--config']
    elif os.getenv('OUTPAK_FILE'):
        return os.getenv('OUTPAK_FILE')
    else:
        return os.path.join(
        os.getcwd(),
        'pak.yml'
    )

def run():
    """Run main command for outpak."""
    console.box("Outpak v{}".format(__version__))
    arguments = docopt(__doc__, version=__version__)

    path = get_path(arguments)

    if arguments['install']:
        config = OutpakConfig(path, arguments)
        if config.is_valid:
            command = OutpakCommand(config=config)
            command.execute()


if __name__ == "__main__":
    run()
