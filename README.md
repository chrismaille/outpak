# Welcome to Outpak's documentation!

[![PyPI](https://img.shields.io/pypi/v/outpak.svg)](https://github.com/chrismaille/outpak)
[![Build Status](https://travis-ci.org/chrismaille/outpak.svg?branch=master)](https://travis-ci.org/chrismaille/outpak)
[![PyPI](https://img.shields.io/pypi/pyversions/outpak.svg)](https://github.com/chrismaille/outpak)
[![Coverage Status](https://coveralls.io/repos/github/chrismaille/outpak/badge.svg)](https://coveralls.io/github/chrismaille/outpak)
[![Documentation Status](https://readthedocs.org/projects/outpak/badge/?version=latest)](http://outpak.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/752016eb6b864a01af676a2c9548090b)](https://www.codacy.com/app/chrismaille/outpak?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=chrismaille/outpak&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/8b21c61fe9130b502add/maintainability)](https://codeclimate.com/github/chrismaille/outpak/maintainability)
[![Requirements Status](https://requires.io/github/chrismaille/outpak/requirements.svg?branch=master)](https://requires.io/github/chrismaille/outpak/requirements/?branch=master)

***

**Read the Docs**: http://outpak.readthedocs.io/

**Source Code**: https://github.com/chrismaille/outpak

**Outpak** is a tool for installing packages inside `requirements.txt` using [Git Personal Tokens](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) or [Bitbucket App Passwords](https://confluence.atlassian.com/bitbucket/app-passwords-828781300.html), instead of using _SSH keys_. This is specially important on [Docker](https://www.docker.com) projects, if you don't want to copy the _SSH keys_ inside the containers.

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

You can also, use the `--quiet` option to run pip in silent mode.

### Further reading

Please check full documentation in [Read the Docs](http://outpak.readthedocs.io/)