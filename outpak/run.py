"""Outpak v1.1.0.

usage: pak [-h] [-q] [-c CONFIG] [-v] {install}

positional arguments:
  {install}

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Calls pip with the -q (quiet) option
  -c CONFIG, --config CONFIG
                        Full path to the config file
  -v, --version         Displays version and quits
G
"""
import os
import argparse
from outpak import __version__
from outpak.main import Outpak


def get_pak_yml_path():
    """Get pak.yml full path.

    Returns
    -------
        Str: full path from current path

    """
    default_path = os.path.join(
        os.getcwd(),
        'pak.yml'
    )
    return os.environ.get('OUTPAK_FILE', None) or default_path


def run():
    """Run main command for outpak."""
    parser = argparse.ArgumentParser(
        description='Outpak v{}'.format(__version__)
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        default=False,
        help='Calls pip with the -q (quiet) option'
    )
    parser.add_argument(
        '-c', '--config',
        default=get_pak_yml_path(),
        required=False,
        help='Full path to the config file'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=__version__,
        help='Displays version and quits'
    )
    parser.add_argument(
        'command',
        choices=['install']
    )

    arguments = parser.parse_args()

    if arguments.command == 'install':
        newpak = Outpak(arguments.config, pip_quiet=arguments.quiet)
        newpak.run()


if __name__ == "__main__":
    run()
