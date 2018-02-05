Welcome to Outpak's documentation!
==================================

.. image:: https://img.shields.io/pypi/v/outpak.svg
	:target: https://pypi.python.org/pypi/outpak
.. image:: https://travis-ci.org/chrismaille/outpak.svg?branch=master
    :target: https://travis-ci.org/chrismaille/outpak
.. image:: https://img.shields.io/pypi/pyversions/outpak.svg
	:target: https://github.com/chrismaille/outpak
.. image:: https://coveralls.io/repos/github/chrismaille/outpak/badge.svg?branch=master
	:target: https://coveralls.io/github/chrismaille/outpak?branch=master
.. image:: https://readthedocs.org/projects/outpak/badge/?version=latest
	:target: http://outpak.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status
.. image:: https://api.codacy.com/project/badge/Grade/752016eb6b864a01af676a2c9548090b    :target: https://www.codacy.com/app/chrismaille/outpak?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=chrismaille/outpak&amp;utm_campaign=Badge_Grade
.. image:: https://api.codeclimate.com/v1/badges/8b21c61fe9130b502add/maintainability
   :target: https://codeclimate.com/github/chrismaille/outpak/maintainability
   :alt: Maintainability

* Read the Docs: http://outpak.readthedocs.io/
* Source Code: https://github.com/chrismaille/outpak

Outpak_ is a tool for installing packages inside ``requirements.txt`` using `Git Personal Tokens`_ or `Bitbucket App Passwords`_, instead of using *SSH keys*. This is specially important on Docker_ projects, if you don't want to copy the *SSH keys* inside the containers.

Install Outpak
-----------------

Install Outpak using the command::

	$ pip install outpak

Create the pak.yml file
--------------------------

For a simple example, let's consider the following environment for your project, loaded in the `.bashrc` file::

	$ export MY_ENVIRONMENT="docker"
	$ export MY_GIT_TOKEN="12345abcde"

Based on these values, we can create the ``pak.yml`` configuration file:

.. code-block:: yaml

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

Save this file on same path where is your ``requirements.txt`` files are located.

Run Outpak
-----------

After create the configuration file, you can start install packages with the command::

	$ pak install --config /path/to/pak/file

If you do not inform the path for the ``pak.yml`` file, Outpak_ will attempt to find it in the current directory. You can also you can set the ``OUTPAK_FILE`` environment variable for where the ``pak.yml`` file is located.

Further reading
---------------

Please check full documentation in http://outpak.readthedocs.io/

.. _Outpak: https://github.com/chrismaille/outpak
.. _Docker: https://www.docker.com
.. _Git Personal Tokens: https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/
.. _Bitbucket App Passwords: https://confluence.atlassian.com/bitbucket/app-passwords-828781300.html