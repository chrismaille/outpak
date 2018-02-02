Introduction
------------

Quick Starting
--------------

Install Outpak using the command::

	$ pip install outpak

Create the ``pak.yml`` configuration file, on the same directory where the ``requirement.txt`` are located.

A single example:

.. code-block:: yaml
	version: "1"
	github_key: MY_GIT_TOKEN
	env_key: MY_ENVIRONMENT
	envs:
	  docker:
	    key_value: docker
	    clone_dir: /opt/src
	    files:
	      - requirements.txt
	      - requirements_test.txt

The ``github_key`` points to the environment variable you use to store your Git Personal Token. (For Bitbucket App Password, use the key ``bitbucket_key``)

The ``env_key`` points to the environment variable which you use to indicate what is the current "working environment": development, virtualenv, stage, production, docker, etc...

For each possible value in the environment variable informed in ``env_key``, you can create a entry in the ``envs`` key:

In our example, if the ``key_value`` of "MY_ENVIROMENT" (the env informed in ``env_var``) was: "docker", the Outpak will use the following data:

* The full path for cloning projects will be ``/opt/src`` as indicated in ``clone_dir`` key.
* The list of files processes will be: ``requirements.txt`` and ``requirements_test.txt`` as indicated in key ``files``.



