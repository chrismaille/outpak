.. Outpak documentation master file, created by
   sphinx-quickstart on Thu Feb  1 22:01:22 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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


This document will guide you how to install, configure and use Outpak_ in your projects.

What is Outpak?
---------------

Outpak_ is a tool for installing packages inside ``requirements.txt`` using `Git Personal Tokens`_ or `Bitbucket App Passwords`_, instead of using *SSH keys*. This is specially important on Docker_ projects, if you don't want to copy the *SSH keys* inside the containers.

For example, if you have on ``requirements.txt`` the following lines::

	-e git+git@git.myproject.org:MyProject#egg=MyProject
	-e git://git.myproject.org/MyProject.git@da39a3ee5e6b4b0d3255bfef95601890afd80709#egg=MyProject

Outpak_ will:

1. Parse the urls::

	from: git+git@git.myproject.org:MyProject or git://git.myproject.org/MyProject.git
	to: https://git.myproject.org/myproject

2. Clone the repositories using the token/password and directory informed in ``pak.yml`` file::

	$ git clone https://my_git_token@git.myproject.org/myproject /tmp/myproject

3. Run `git reset` to correct commit if informed::

	$ cd /tmp/myproject && git reset --hard da39a3ee5e6b4b0d3255bfef95601890afd80709

4. And installing package using  the``pip install -e .`` command::

	$ cd /tmp/myproject && pip install -e .

.. note:: Outpak_ are tested for Bitbucket and Github services. For other DVCS services please check our `issues page`_ on github.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial
   reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _issues page: https://github.com/chrismaille/outpak/issues
.. _Outpak: https://github.com/chrismaille/outpak
.. _Docker: https://www.docker.com
.. _Git Personal Tokens: https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/
.. _Bitbucket App Passwords: https://confluence.atlassian.com/bitbucket/app-passwords-828781300.html