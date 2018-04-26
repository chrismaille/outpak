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
        self.git_token = ""
        self.bit_token = ""
        self.run_silently = False

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

        try:
            ret = ret.decode('utf-8')
        except AttributeError:
            pass

        return True if not get_stdout else ret

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
            if not self.data.get('token_key') and\
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
                self.git_token = os.getenv(git_var)

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
                self.bit_token = os.getenv(bit_var)
        if not git_var and not bit_var:
            console.error(
                "You need to define at least one of "
                "github_key or bitbucket_key in pak.yml"
            )
            sys.exit(1)

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

    def parse_line(self, line):
        """Parse requirements line engine.

        Read the line from requirements.txt, ignoring # commments.

        Ignore if "-r" requirement is found.

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
        line = line.split(" #")[0]  # removing comments (need space)
        line = line.strip().replace("\n", "").replace(" ", "")
        data = {
            "name": None,
            "signal": None,
            "version": None,
            "url": None,
            "head": None,
            "egg": None,
            "line": None,
            "using_line": False,
            "option": ""
        }
        if line.startswith("-r"):
            console.warning("Line {} ignored.".format(line))
            sys.exit(1)

        if line.startswith('-'):
            data['option'] = line[0:2]
            if data['option'] != "-e":
                data['line'] = line
                data['using_line'] = True
            line = line[2:]

        # SomeProject ==5.4 ; python_version < '2.7'
        if ";" in line:
            data['name'] = line.split(";")[0]
            data['using_line'] = True
            data['line'] = original_line
            return data

        # SomeProject0==1.3
        # SomeProject >=1.2,<.2.0
        # SomeProject~=1.4.2
        # SomeProject[foo]>=2.18.1
        # FooProject>=1.2--global-option="--no-user-cfg"
        m = re.search(r"(.+)(>|=|~|<)=(\S+)", line)
        if m:
            data["name"] = m.group(1)
            data["signal"] = m.group(2)
            data["version"] = m.group(3)
            return data

        # SomeProject[foo, bar]
        m = re.search(r"(.+\[.+\])", line)
        if m:
            data["name"] = m.group(1)
            return data

        # SomeProject
        # .packages/my_package
        if "+" not in line and "//" not in line:
            data['name'] = line
            data['line'] = line
            data['using_line'] = True
            return data

        # hg+http://hg.myproject.org/MyProject#egg=MyProject
        # svn+http://svn.myproject.org/svn/MyProject/trunk@2019#egg=MyProject
        # bzr+lp:MyProject#egg=MyProject
        if "hg+" in line or "svn+" in line or "bzr+" in line:
            data['name'] = line
            data['line'] = line
            data['using_line'] = True
            return data

        if line.startswith('git'):
            # git://git.myproject.org/MyProject#egg=MyProject
            # git://git.myproject.org/MyProject@1234acbd#egg=MyProject
            # git+git://git.myproject.org/MyProject#egg=MyProject
            # git+git://git.myproject.org/MyProject@1234abcd#egg=MyProject
            m = re.search(r"(git:\/\/)(.+)#", line)
            if m:
                data['url'] = m.group(2).replace(".git", "")
                if "@" in data['url']:
                    data['head'] = data['url'].split("@")[-1]
                    data['url'] = data['url'].split("@")[0]
                data['name'] = data['url'].split("/")[-1]
                return data

            # git+https://git.myproject.org/MyProject#egg=MyProject
            # git+https://git.myproject.org/MyProject@1234abcd#egg=MyProject
            # git+ssh://git.myproject.org/MyProject#egg=MyProject
            # git+ssh://git.myproject.org/MyProject@1234abcd#egg=MyProject
            m = re.search(r"(git\+\w+:\/\/)(.+)#", line)
            if m:
                data['url'] = m.group(2).replace(".git", "")
                if "@" in data['url']:
                    data['head'] = data['url'].split("@")[-1]
                    data['url'] = data['url'].split("@")[0]
                data['name'] = data['url'].split("/")[-1]
                return data

            # git+git@git.myproject.org:MyProject#egg=MyProject
            # git+git@git.myproject.org:MyProject@1234abcd#egg=MyProject
            m = re.search(r"(git\+git@)(.+)#", line)
            if m:
                data['url'] = m.group(2).replace(".git", "").replace(":", "/")
                if "@" in data['url']:
                    data['head'] = data['url'].split("@")[-1]
                    data['url'] = data['url'].split("@")[0]
                data['name'] = data['url'].split("/")[-1]
                return data

        # https://git.myproject.org/MyProject#egg=MyProject
        # https://git.myproject.org/MyProject@commit1234#egg=MyProject
        if line.startswith("http"):
            data['line'] = line.split("#")[0]
            data['using_line'] = True
            data['name'] = data['line'].split("@")[0].split("/")[-1]
            return data

        console.error('Cannot parse: {}'.format(original_line))
        sys.exit(1)

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
        if 'bitbucket' in package['url']:
            ret = self._run_command(
                "cd {} && git clone https://{}@{}".format(
                    temp_dir, self.bit_token, package['url']),
                verbose=True
            )
        else:
            ret = self._run_command(
                "cd {} && git clone https://{}@{}".format(
                    temp_dir, self.git_token, package['url']),
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
                "cd {} && pip install {}{}.".format(
                    full_package_path,
                    "-q " if self.run_silently and package['option'] is not '-q' else "",
                    "{} ".format(package['option']) if package['option'] else ""
                ),
                verbose=True
            )
        if not ret:
            sys.exit(1)

    def _install_with_pip(self, package):
        if package['using_line']:
            task = 'pip install {}"{}"'.format(
                '-q ' if self.run_silently else '',
                package['line']
            )
        else:
            task = "pip install {}{}{}{}{}{}{}".format(
                '-q ' if self.run_silently else '',
                "{} ".format(package['option']) if package['option'] else "",
                package['name'],
                '"' if package['signal'] and
                package['signal'] != "=" else "",
                "{}=".format(
                    package['signal']) if package['signal'] else "",
                package['version'] if package['version'] else "",
                '"' if package['signal'] and
                package['signal'] != "=" else "",
            )
        ret = self._run_command(
            task=task,
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
            'using Token' if package['url'] else "using pip{}".format(' (silent)' if self.run_silently else '')
        ), use_prefix=False)

        if package['url'] and not package['using_line']:
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
            console.info("Reading {}.".format(file))

            with open(file) as reqfile:
                file_list = []
                read_line = ""
                for line in reqfile:
                    if line.strip().startswith("#") or \
                            line.strip().startswith("-r") or \
                            line.strip().replace("\n", "") == "":
                        continue
                    if "\\" in line:
                        read_line += "".join(
                            line.strip().split("\\")[0]
                        )
                        continue
                    elif not read_line:
                        read_line = line
                    read_line = read_line.replace("\n", "").strip()
                    if read_line != "":
                        file_list.append(self.parse_line(read_line))
                    read_line = ""
            package_list += file_list

        for package in package_list:
            self.install_package(package)
