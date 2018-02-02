Pak.yml Reference
=================

This is the reference documentation for the pak.yml file.

Reference List
--------------
* :ref:`bitbucket_key`
* :ref:`clone_dir`
* :ref:`env_key`
* :ref:`envs`
* :ref:`files`
* :ref:`github_key`
* :ref:`key_value`
* :ref:`token_key`
* :ref:`use_virtual`
* :ref:`version`

.. _bitbucket_key:

bitbucket_key
.............

Set the environment variable which holds your `Bitbucket App Password`_

.. _Bitbucket App Password: https://confluence.atlassian.com/bitbucket/app-passwords-828781300.html

.. code-block:: yaml

  bitbucket_key: MY_BITBUCKET_APP_PASSWORD

In the environment key you set the app password: ``MY_BITBUCKET_APP_PASSWORD="username:password"`` 

.. note:: The format for the bitbucket app password in the environment key must be: ``username:password``.

.. _clone_dir:

clone_dir
.........

Set the base path where the projects will be cloned:

.. code-block:: yaml

  envs:
    virtualenv:
      clone_dir: /tmp

Outpak_ will generate a full path for each project, using the base path provided and the project name found in url:

For example, if url is *git+git@git.myproject.org:MyProject* and *clone_dir* is ``/tmp`` the cloning path will be ``/tmp/myproject``.

You need to inform a full path, do not use relative paths.

.. note:: Make sure the current user can be the right permissions to save in this directory.

.. _env_key:

env_key
.......

Set the environment variable which control your Project environment.

.. code-block:: yaml

  env_key: MY_ENVIRONMENT_KEY


.. _envs:

envs
....

Returns a list of possible values for the enviroment key defined ``env_key``:

.. code-block:: yaml

  env_key: MY_ENVIRONMENT_KEY
  envs:
    Virtualenv:
      key_value: development
    Docker:
      key_value: docker
    Staging:
      key_value: stage
    Production:
      key_value: prod

At least one enviroment must be set.

.. note:: Make sure you have create entries for all possible values for your environment key.

.. _files:

files
.....

Returns a list of ``requirement.txt`` files must be processed for each enviroment defined:

.. code-block:: yaml

  env_key: MY_ENVIRONMENT_KEY
  envs:
    Dev:
      key_value: development
      files:
        - requirements.txt
        - requirements_test.txt
    Prod:
      key_value: prod
      files:
        - requirements.txt


.. _github_key:

github_key
..........

Set the environment variable which holds your `Git Personal Token`_

.. _Git Personal Token: https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/

.. code-block:: yaml

  github_key: MY_GIT_PERSONAL_TOKEN

.. _key_value:

key_value
.........

OutPak_ will get value found inside the environment variable you define in ``env_key`` to find the correct env to process the ``requirement.txt`` files.

.. code-block:: yaml

  env_key: MY_ENVIRONMENT_KEY
  envs:
    Virtualenv:
      key_value: development
      clone_dir: /tmp
    Docker:
      key_value: docker
      clone_dir: /opt/src
    Staging:
      key_value: stage
      clone_dir: /opt/src
    Production:
      key_value: prod
      clone_dir: /opt/src

For example, if the env ``MY_ENVIRONMENT_KEY="development"``, then Outpak_ will use the ``/tmp`` as base path for cloning projects.

.. _token_key:

token_key
.........

Same as :ref:`github_key`.

.. note:: This key is deprecated and will be removed in next version.

.. _use_virtual:

use_virtual
...........

Set if Outpak_ need to check if a virtualenv was activated, before start processing the ``requirement.txt`` files:

.. code-block:: yaml

  version: "1"
  env_key: MY_ENVIRONMENT_KEY
  envs:
    Prod:
      key_value: production
      clone_dir: /opt/src
    Dev:
      key_value: development
      use_virtual: true
      clone_dir: /tmp


.. _version:

version
.......

Set the version for this file. Current version is: "1"

.. code-block:: yaml

  version: "1"


.. _Outpak: https://github.com/chrismaille/outpak