"""Outpak Utils module."""
import os
import re
import sys

import yaml
from buzio import console

path_matcher = re.compile(r'\$[{]?([A-Za-z-_]+)[}]?')


def path_constructor(loader, node):
    """Pyaml Path Constructor."""
    value = node.value
    match = path_matcher.match(value)
    env_var = match.group()[1:]
    value = os.environ.get(env_var, None)
    return value


yaml.add_implicit_resolver('!path', path_matcher, None, yaml.SafeLoader)
yaml.add_constructor('!path', path_constructor, yaml.SafeLoader)


def load_from_yaml(path):
    """Load data from pak.yml."""
    try:
        with open(path, 'r') as file:
            data = yaml.safe_load(file.read())
            return data
    except IOError as exc:
        console.error("Cannot open file: {}".format(exc))
        sys.exit(1)
    except yaml.YAMLError as exc:
        console.error("Cannot read file: {}".format(exc))
        sys.exit(1)
    except Exception as exc:
        console.error("Error: {}".format(exc))
        sys.exit(1)
