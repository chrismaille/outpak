import os
import sys

from buzio import console

from outpak.parser.pip import PipParser


def get_parser_for(file):
    extension = os.path.splitext(file)[-1]
    if 'txt' in extension:
        return PipParser()

    console.error("File {} not recognized.".format(file))
    sys.exit(1)