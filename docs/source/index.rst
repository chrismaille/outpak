.. Outpak documentation master file, created by
   sphinx-quickstart on Thu Feb  1 22:01:22 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Outpak's documentation!
==================================

.. image:: https://img.shields.io/pypi/v/nine.svg
	:target: https://pypi.python.org/pypi/outpak
.. image:: https://travis-ci.org/chrismaille/outpak.svg?branch=master
    :target: https://travis-ci.org/chrismaille/outpak
.. image:: https://img.shields.io/pypi/pyversions/outpak.svg
	:target: https://github.com/chrismaille/outpak
.. image:: https://coveralls.io/repos/github/chrismaille/outpak/badge.svg?branch=master
	:target: https://coveralls.io/github/chrismaille/outpak?branch=master

This document will guide you how to install, configure and use Outpak_ in your projects.

What is Outpak?
---------------

Outpak_ is a tool for installing packages inside ``requirements.txt`` using *Git Personal Tokens* or **Bitbucket App Passwords**, instead of using `SSH keys`.

This is specially important on Docker_ projects, when the SSH keys are not inside the containers.

For those examples inside ``requirements.txt``::

	-e git+git@git.myproject.org:MyProject#egg=MyProject
	-e git://git.myproject.org/MyProject.git@da39a3ee5e6b4b0d3255bfef95601890afd80709#egg=MyProject


Outpak_ will parse the url, clone the repositories using the token/password, git reset to correct commit when informed, and installing it using pip.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   tutorial
   reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Outpak: https://github.com/chrismaille/outpak
.. _Docker: https://www.docker.com