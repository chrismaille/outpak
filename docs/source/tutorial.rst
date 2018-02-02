Tutorial
========

This document will explain how to install Outpak_ and make the first use in your project.

Installing Outpak
-----------------

First, install Outpak using the command::

	$ pip install outpak


Creating the pak.yml file
--------------------------

Then, for a simple example, let's consider the following environment for your project, loaded in the `.bashrc` file::

	$ export MY_ENVIRONMENT="docker"
	$ export MY_GIT_TOKEN="12345abcde"


Based on these values, we can create the ``pak.yml`` configuration file:

.. code-block:: YAML

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

.. note:: Save the pak.yml on the same directory where the ``requirements.txt`` files are located.

The ``github_key``
..................
The ``github_key`` points to the environment variable you use to store your `Git Personal Token`_. (For `Bitbucket App Password`_, use the key ``bitbucket_key``). On our example is the **MY_GIT_TOKEN** env.

The ``env_key``
...............
The ``env_key`` points to the environment variable which you use to indicate what is the project current *working environment* (*development*, *stage*, *etc*...). In our example is the **MY_ENVIRONMENT** env.

The ``envs`` key
................
The ``envs`` list can hold one entry per possible value the **MY_ENVIRONMENT** (the ``env_key``) holds. In our example, **MY_ENVIRONMENT** was set to "docker", so we need a "Docker" entry in this key: 

	* The ``key_value`` must be the same value stored in the **MY_ENVIRONMENT** var: in our example "docker"
	* The full path for cloning projects will be ``/opt/src`` as indicated in ``clone_dir`` key.
	* The list of files which will be processed are: ``requirements.txt`` and ``requirements_test.txt`` as indicated in key ``files``.

.. note:: Check the :doc:`reference` page to the complete reference for ``pak.yml`` files.

Running Outpak
--------------

After create the configuration file, you can start install packages with the command::

	$ pak install --config /path/to/pak/file

If you do not inform the path for the ``pak.yml`` file, Outpak_ will attempt to find it in the current directory.

.. note:: Also you can set the ``OUTPAK_FILE`` environment variable for where the ``pak.yml`` file is located.


.. _Outpak: https://github.com/chrismaille/outpak
.. _Git Personal Token: https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/
.. _Bitbucket App Password: https://confluence.atlassian.com/bitbucket/app-passwords-828781300.html
