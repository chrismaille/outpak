import os
import sys

import yaml
from buzio import console


class OutpakConfig:
    def __init__(self, path, arguments):
        self.path = path
        self.arguments = arguments
        self.data = {}
        self.environment = None
        self.github_token = None
        self.bitbucket_token = None
        self.requirement_files = []

    @property
    def is_valid(self):
        self._load_from_yaml()
        self._validate_data_from_yaml()
        self._get_outpak_work_environment()
        self._get_token()
        self._get_files()
        self._check_venv()
        return True

    @property
    def run_silently(self):
        return self.arguments['--quiet'] or bool(os.getenv('OUTPAK_RUN_SILENTLY'))

    @property
    def default_index_url(self):
        """Return index URL.

        Order is:
        1. Index URL in Yaml Environment.
        2. Index URL in Yaml Default.
        3. Index URL in Memory.
        """
        return self.environment.get('index_url') or self.data.get('index_url') or os.getenv('PIP_INDEX_URL')

    @property
    def extra_indexes(self):
        return self.environment.get('extra_indexes', [])

    @property
    def clone_dir(self):
        return self.environment['clone_dir']

    def _load_from_yaml(self):
        """Load data from pak.yml."""
        try:
            with open(self.path, 'r') as file:
                self.data = yaml.load(file.read())
        except IOError as exc:
            console.error("Cannot open file: {}".format(exc))
            sys.exit(1)
        except yaml.YAMLError as exc:
            console.error("Cannot read file: {}".format(exc))
            sys.exit(1)
        except Exception as exc:
            console.error("Error: {}".format(exc))
            sys.exit(1)

    def _validate_data_from_yaml(self):
        """Validate data from pak.yml."""
        error = False
        if not self.data.get("version"):
            error = True
            console.error("You must define version in {}".format(self.path))
        elif self.data['version'] == "1":
            if not self.data.get('token_key') and \
                    not self.data.get('github_key') and \
                    not self.data.get('bitbucket_key'):
                error = True
                console.error(
                    "You must define environment "
                    "variable for Git Token or "
                    "Bitbucket App Password in {}".format(
                        self.path))
            if not self.data.get('env_key'):
                error = True
                console.error(
                    "You must define environment "
                    "variable for Project Environment in {}".format(
                        self.path))
            if not self.data.get('envs'):
                error = True
                console.error(
                    "You must configure at least "
                    "one Project Environment in {}".format(
                        self.path))
            else:
                for env in self.data['envs']:
                    key_list = ['key_value', 'clone_dir', 'files']
                    for key in key_list:
                        if key not in self.data['envs'][env].keys():
                            error = True
                            console.error(
                                "You must define the "
                                "{} key inside {} environment".format(
                                    key, env))
        else:
            error = True
            console.error("Wrong version in {}".format(self.path))
        if error:
            sys.exit(1)

    def _get_outpak_work_environment(self):
        """Get current environment.

        Check the value for env_key informed,
        and select  correspondent key inside the pak.yml file.

        Example
        -------
            pak.yml:
                env_key: MY_ENVIRONMENT
                envs:
                    prod:
                        key_value: production
                        ...
                    dev:
                        key_value: development
                        ...

            if MY_ENVIROMENT=development
            code will save the 'dev' key in self.environment

        """
        env_var = self.data['env_key']
        if not os.getenv(env_var):
            console.error('Please set {}'.format(env_var))
            sys.exit(1)
        else:
            value = os.getenv(env_var)
            environment_data = [
                data
                for data in self.data['envs']
                if self.data['envs'][data]['key_value'] == value
            ]
            if environment_data:
                self.environment = self.data['envs'][environment_data[0]]
                console.info(
                    "Using configuration for environment: {}".format(
                        environment_data[0]))
            else:
                console.error(
                    "Not found configuration for {} environment."
                    " Please check {}".format(
                        value, self.path))
                sys.exit(1)

    def _get_token(self):
        """Get current token.

        Check the value for env_key informed,
        and select correspondent key inside the pak.yml file.

        Example
        -------
            pak.yml:
                github_key: MY_GIT_TOKEN

            if MY_GIT_TOKEN=1234-5678
            code will save the '1234-5678' in self.git_token

        """
        git_var = self.data.get('github_key')
        if not git_var:
            git_var = self.data.get('token_key')
        if git_var:
            if not os.getenv(git_var):
                console.error(
                    "Please set your {} "
                    "(https://github.com/settings/tokens)".format(git_var))
                sys.exit(1)
            else:
                self.github_token = os.getenv(git_var)

        bit_var = self.data.get('bitbucket_key')
        if bit_var:
            if not os.getenv(bit_var):
                console.error(
                    "Please set your {} "
                    "(https://bitbucket.org/account/user"
                    "/<your_user>/app-passwords)".format(bit_var))
                sys.exit(1)
            else:
                if ":" not in os.getenv(bit_var):
                    console.error(
                        "For Bitbucket "
                        "Password App format is username:password"
                    )
                    sys.exit(1)
                self.bitbucket_token = os.getenv(bit_var)
        if not git_var and not bit_var:
            console.error(
                "You need to define at least one of "
                "github_key or bitbucket_key in pak.yml"
            )
            sys.exit(1)

    def _get_files(self):
        """Return existing files from list.

        Returns
        -------
            List: full path for existing files

        """
        current_path = os.path.dirname(self.path)
        file_list = [
            os.path.join(current_path, filename)
            for filename in self.environment['files']
            if os.path.isfile(os.path.join(current_path, filename))
        ]
        self.requirement_files = file_list
        if not self.requirement_files:
            console.error('No requirement files found.')
            sys.exit(1)

    def _check_venv(self):
        """Check if virtualenv is active."""

        def is_venv():
            return (
                    hasattr(sys, 'real_prefix') or  # virtualenv
                    (
                            hasattr(sys, 'base_prefix') and
                            sys.base_prefix != sys.prefix  # pyvenv
                    )
            )

        if self.environment.get('use_virtual', False):
            if is_venv():
                virtual = sys.prefix
                console.info(
                    "Running in virtual environment: {}".format(virtual))
            else:
                console.error("Virtual environment not found")
                sys.exit(1)
        console.info("Pip is {}".format(self.get_pip_version()))
        console.info("Python is {}".format(sys.version))

    def get_pip_version(self):
        ret = console.run('pip --version', get_stdout=True).replace('\n', '')
        return ret.split(' ')[1]
