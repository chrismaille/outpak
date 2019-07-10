"""Outpak Version 1."""
import os
import sys

from buzio import console

from outpak.main.base import BaseOutpak


class Outpak(BaseOutpak):
    """Outpak Class.

    Attributes
    ----------
        data (dict): data from pak.yml
        environment (dict): dictionary data from current environment
        path (string): full path for pak.yml
        token (string): git token from environment variable

    """

    environment: dict
    version = "1"

    def __init__(self, config_path: str, config_data: dict) -> None:
        """Initialize class.

        :param config_path: path for pak.yml file
        :param config_data: data from pak.yml file
        """
        super(Outpak, self).__init__(config_path, config_data)
        self.git_token = ""
        self.bit_token = ""

    def validate_data(self) -> None:
        """Validate data from pak.yml."""
        error = False
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

        if error:
            sys.exit(1)

    def get_current_environment(self) -> None:
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

    def get_token(self) -> None:
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
                self.git_token = os.getenv(git_var, "")

        bit_var = self.data.get('bitbucket_key')
        if bit_var:
            if not os.getenv(bit_var):
                console.error(
                    "Please set your {} "
                    "(https://bitbucket.org/account/user"
                    "/<your_user>/app-passwords)".format(bit_var))
                sys.exit(1)
            else:
                if ":" not in os.getenv(bit_var, ""):
                    console.error(
                        "For Bitbucket "
                        "Password App format is username:password"
                    )
                    sys.exit(1)
                self.bit_token = os.getenv(bit_var, "")
        if not git_var and not bit_var:
            console.error(
                "You need to define at least one of "
                "github_key or bitbucket_key in pak.yml"
            )
            sys.exit(1)

    def check_venv(self) -> None:
        """Check if virtualenv is active."""

        def is_venv() -> bool:
            return (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and
                                                    sys.base_prefix != sys.prefix))

        if self.environment.get('use_virtual', False):
            if is_venv():
                virtual = sys.prefix
                console.info(
                    "Running in virtual environment: {}".format(virtual))
            else:
                console.error("Virtual environment not found")
                sys.exit(1)

    def install(self):
        """Run instance."""
        self.get_current_environment()
        self.get_token()
        self.check_venv()

        file_list = self.get_files(file_list=self.environment['files'])
        self._execute_install(file_list)
