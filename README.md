# Welcome to Outpak's documentation!

[![PyPI](https://img.shields.io/pypi/v/nine.svg)](https://github.com/chrismaille/outpak)
[![Build Status](https://travis-ci.org/chrismaille/outpak.svg?branch=master)](https://travis-ci.org/chrismaille/outpak)
[![PyPI](https://img.shields.io/pypi/pyversions/outpak.svg)](https://github.com/chrismaille/outpak)
[![Coverage Status](https://coveralls.io/repos/github/chrismaille/outpak/badge.svg)](https://coveralls.io/github/chrismaille/outpak)
[![Documentation Status](https://readthedocs.org/projects/outpak/badge/?version=latest)](http://outpak.readthedocs.io/en/latest/?badge=latest)

**Read the Docs**: http://outpak.readthedocs.io/

**Source Code**: https://github.com/chrismaille/outpak

_Outpak_ is a tool for installing packages inside `requirements.txt` using [Git Personal Tokens]() or [Bitbucket App Passwords](), instead of using _SSH keys_. This is specially important on [Docker]() projects, if you don't want to copy the _SSH keys_ inside the containers.

### Install Outpak

Install Outpak using the command:

```bash
$ pip install outpak
```

### Create the pak.yml file

For a simple example, let's consider the following environment for your project, loaded in the `.bashrc` file:

```bash
$ export MY_ENVIRONMENT="docker"
$ export MY_GIT_TOKEN="12345abcde"
```

Based on these values, we can create the `pak.yml` configuration file:

```yaml
    version: "1"
    github_key: MY_GIT_TOKEN
    env_key: MY_ENVIRONMENT
    envs:
      Docker:
        key_value: docker
        clone_dir: /opt/src
        files:
          - requirements.txt
          - requirements_test.txt
```

Save this file on same path where is your `requirements.txt` files are located.

### Run Outpak

After create the configuration file, you can start install packages with the command:

```bash
$ pak install --config /path/to/pak/file
```

If you do not inform the path for the `pak.yml` file, Outpak_ will attempt to find it in the current directory. You can also you can set the `OUTPAK_FILE` environment variable for where the `pak.yml` file is located.