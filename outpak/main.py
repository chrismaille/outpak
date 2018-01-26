"""Outpak main module."""
import os
import re
import shutil
import subprocess
import sys
import yaml
from buzio import console


class Outpak():
    """Outpak Class.

    Attributes
    ----------
        data (dict): data from pak.yml
        environment (dict): dictionary data from current environment
        path (string): full path for pak.yml
        token (string): git token from environment variable

    """

    def __init__(self, path, *args, **kwargs):
        """Initialize class.

        Args:
            path (sring): full path from click option (-c)
        """
        self.path = path

    def _run_command(
            self,
            task,
            title=None,
            get_stdout=False,
            run_stdout=False,
            verbose=False,
            silent=False):
        """Run command in subprocess.

        Args:
            task (string): command to run
            title (string, optional): title to be printed
            get_stdout (bool, optional): return stdout from command
            run_stdout (bool, optional): run stdout before command
            verbose (bool, optional): show command in terminal
            silent (bool, optional): occult stdout/stderr when running command

        Return
        ------
            Bool or String: Task success or Task stdout

        """
        if title:
            console.section(title)

        try:
            if run_stdout:
                if verbose:
                    console.info(task, use_prefix=False)
                command = subprocess.check_output(task, shell=True)

                if not command:
                    print('An error occur. Task aborted.')
                    return False

                if verbose:
                    console.info(command, use_prefix=False)
                ret = subprocess.call(command, shell=True)

            elif get_stdout is True:
                if verbose:
                    console.info(task, use_prefix=False)
                ret = subprocess.check_output(task, shell=True)
            else:
                if verbose:
                    console.info(task, use_prefix=False)
                ret = subprocess.call(
                    task if not silent else
                    "{} 2>/dev/null 1>/dev/null".format(task),
                    shell=True,
                    stderr=subprocess.STDOUT)

            if ret != 0 and not get_stdout:
                return False
        except BaseException:
            return False

        return True if not get_stdout else ret.decode('utf-8')

    def load_from_yaml(self):
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

    def validate_data_from_yaml(self):
        """Validate data from pak.yml."""
        error = False
        if not self.data.get("version"):
            error = True
            console.error("You must define version in {}".format(self.path))
        elif self.data['version'] == "1":
            if not self.data.get('token_key'):
                error = True
                console.error(
                    "You must define environment "
                    "variable for Git Token in {}".format(
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

    def get_current_environment(self):
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

    def get_token(self):
        """Get current token.

        Check the value for env_key informed,
        and select correspondent key inside the pak.yml file.

        Example
        -------
            pak.yml:
                token_key: MY_GIT_TOKEN

            if MY_GIT_TOKEN=1234-5678
            code will save the '1234-5678' in self.token

        """
        token_var = self.data['token_key']
        if not os.getenv(token_var):
            console.error(
                "Please set your {} "
                "(https://github.com/settings/tokens)".format(token_var))
            sys.exit(1)
        else:
            self.token = os.getenv(token_var)

    def get_files(self):
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
        return file_list

    def check_venv(self):
        """Check if virtualenv is active."""
        if self.environment.get('use_virtual', False):
            if hasattr(sys, 'real_prefix'):
                virtual = sys.prefix
                console.info(
                    "Running in virtual environment: {}".format(virtual))
            else:
                console.error("Virtual environment not found")
                sys.exit(1)

    def parse_line(self, line):
        """Parse requirements line engine.

        Read the line from requirements.txt, ignoring # commments.

        Gives an error if "-r" requirement is found.

        Check order is:

        1. Check for fixed requirements (ex.: requests==2.18.4)
        2. Check for latest requirements (ex.: django)
        3. Check for "-e" requirements:
            a) non secure links (ex.: -e ./packages/my_package)
            # egg=my_package_egg)
            b) git+https packages
            (ex.: -e git+https://github.com/my_group/my_pack@commit#egg=my_egg)
            c) git+git packages
            (ex.: -e git+git@github.com:my_group/my_pack@commit#egg=my_egg)

        Gives an error if line cannot be parsed.

        Args:
            line (string): line from requirements.txt

        Returns
        -------
            Dict: data dictionary for package

            Example 1: django==2.0.1
            returns {
                "name": "django",
                "signal: "=",
                "version": "2.0.1",
                "head": None,
                "egg": None
            }

            Example 2:
            -e git+git@github.com:my_group/my_pack@my_commit#egg=my_package_egg
            returns {
                "name": "my_pack",
                "signal: None,
                "version": None,
                "head": "my_commit",
                "egg": "my_package_egg"
            }

        """
        original_line = line
        line = line.split(" #")[0]  # removing comments
        line = line.strip().replace("\n", "").replace(" ", "")
        data = {
            "name": None,
            "signal": None,
            "version": None,
            "url": None,
            "head": None,
            "egg": None
        }
        if line.startswith("-r"):
            console.error(
                "Option -r inside file is not allowed. "
                "Please add requirements "
                "files in pak.yml".format(original_line))
        # Fixed requirement
        elif not line.startswith('-e'):
            m = re.search(r"(.+)(>|=)=(\S+)", line)
            if m:
                data["name"] = m.group(1)
                data["signal"] = m.group(2)
                data["version"] = m.group(3)
            # Latest requirement
            else:
                if not line.startswith("-"):
                    m = re.search(r"(.+)(\n|\r|$)", line)
                    if m:
                        data["name"] = m.group(1)
        # edit packages
        elif line.startswith('-e'):
            # non-secure links
            if "git+" not in line:
                data['name'] = line.replace("\n", "")
            # -e git+https package
            elif "http" in line:
                m = re.search(r"(\/\/)(.+)@(.+)#egg=(.+)", line)
                if m:
                    data['name'] = m.group(2).split("/")[-1]
                    data['url'] = m.group(2)
                    data['head'] = m.group(3)
                    data['egg'] = m.group(4)
                else:
                    m = re.search(r"(\/\/)(.+)#egg=(.+)", line)
                    if m:
                        data['name'] = m.group(2).split("/")[-1]
                        data['url'] = m.group(2)
                        data['egg'] = m.group(3)
                    else:
                        m = re.search(r"(\/\/)(.+)@(.+)", line)
                        if m:
                            data['name'] = m.group(2).split("/")[-1]
                            data['url'] = m.group(2)
                            data['head'] = m.group(3)
                        else:
                            m = re.search(r"(\/\/)(.+)", line)
                            if m:
                                data['name'] = m.group(2).split("/")[-1]
                                data['url'] = m.group(2)
            # -e git+git package
            elif "git+git" in line:
                m = re.search(r"git@(.+)@(.+)#egg=(.+)", line)
                if m:
                    data['name'] = m.group(1).split(
                        "/")[-1].replace(".git", "")
                    data['url'] = m.group(1).replace(":", "/")
                    data['head'] = m.group(2)
                    data['egg'] = m.group(3)
                else:
                    m = re.search(r"git@(.+)#egg=(.+)", line)
                    if m:
                        data['name'] = m.group(1).split(
                            "/")[-1].replace(".git", "")
                        data['url'] = m.group(1).replace(":", "/")
                        data['egg'] = m.group(3)
                    else:
                        m = re.search(r"git@(.+)", line)
                        if m:
                            data['name'] = m.group(1).split(
                                "/")[-1].replace(".git", "")
                            data['url'] = m.group(1).replace(":", "/")

        if not data['name']:
            console.error('Cannot parse: {}'.format(original_line))
            sys.exit(1)
        return data

    def _create_clone_dir(self, package):
        temp_dir = os.path.join(
            self.environment['clone_dir'],
            package['name']
        )
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        return temp_dir

    def _install_with_url(self, package):
        temp_dir = self._create_clone_dir(package)
        full_package_path = os.path.join(temp_dir, package['name'])
        ret = self._run_command(
            "cd {} && git clone https://{}@{}".format(
                temp_dir, self.token, package['url']),
            verbose=True
        )
        if ret and package['head']:
            branchs = self._run_command(
                'cd {} && git fetch --all && git branch -a'.format(
                    full_package_path),
                get_stdout=True
            )
            if branchs and package['head'] in branchs:
                ret = self._run_command(
                    "cd {} && git checkout {}".format(
                        full_package_path, package['head']),
                    verbose=True
                )
            else:
                ret = self._run_command(
                    "cd {} && git reset --hard {}".format(
                        full_package_path, package['head']),
                    verbose=True
                )
        if ret:
            ret = self._run_command(
                "cd {} && pip install -e .".format(full_package_path),
                verbose=True
            )
        if not ret:
            sys.exit(1)

    def _install_with_pip(self, package):
        ret = self._run_command(
            "pip install {}{}{}{}{}".format(
                package['name'],
                '"' if package['signal'] and
                package['signal'] != "=" else "",
                "{}=".format(
                    package['signal']) if package['signal'] else "",
                package['version'] if package['version'] else "",
                '"' if package['signal'] and
                package['signal'] != "=" else "",
            ),
            verbose=True
        )
        if not ret:
            sys.exit(1)

    def install_package(self, package):
        """Install parsed package.

        Args:
            package (dict): Data parsed from package in requirements.txt
        """
        console.section("Installing {} ({}{})".format(
            package['name'],
            package['signal'] if package['signal'] and
            package['signal'] != "=" else "",
            package['version'] if package['version'] else "latest"
        ))
        console.info("Installing {}{}".format(
            "at head {} ".format(package['head']) if package['head'] else "",
            'using Token' if package['url'] else "using pip"
        ), use_prefix=False)

        if package['url']:
            self._install_with_url(package)
        else:
            self._install_with_pip(package)

    def run(self):
        """Run instance."""
        self.load_from_yaml()
        self.validate_data_from_yaml()
        self.get_current_environment()
        self.get_token()
        self.check_venv()

        file_list = self.get_files()
        if not file_list:
            sys.exit(0)

        package_list = []
        for file in file_list:
            console.info("Reading {}...".format(file))

            with open(file) as reqfile:
                file_list = [
                    self.parse_line(line)
                    for line in reqfile
                    if line.replace("\n", "").strip() != "" and
                    not line.replace("\n", "").strip().startswith("#")
                ]
            package_list += file_list

        for package in package_list:
            self.install_package(package)
