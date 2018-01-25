import os
import re
import shutil
import subprocess
import sys
import yaml
from buzio import console


class Outpak():

    def __init__(self, path, *args, **kwargs):
        self.path = path

    def _run_command(
            self,
            task,
            title=None,
            get_stdout=False,
            run_stdout=False,
            verbose=False,
            silent=False):
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
                    task if not silent else "{} 2>/dev/null 1>/dev/null".format(task),
                    shell=True,
                    stderr=subprocess.STDOUT
                )

            if ret != 0 and not get_stdout:
                return False
        except BaseException:
            return False

        return True if not get_stdout else ret.decode('utf-8')

    def _load_from_config(self):
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

    def _check_config_from_version(self):
        error = False
        if not self.data.get("version"):
            error = True
            console.error("You must define version in {}".format(self.path))
        elif self.data['version'] == "1":
            if not self.data.get('token_key'):
                error = True
                console.error("You must define environment variable for Git Token in {}".format(self.path))
            if not self.data.get('env_key'):
                error = True
                console.error("You must define environment variable for Project Environment in {}".format(self.path))
            if not self.data.get('envs'):
                error = True
                console.error("You must configure at least one Project Environment in {}".format(self.path))
            else:
                for env in self.data['envs']:
                    key_list = ['key_value', 'clone_dir', 'files']
                    for key in key_list:
                        if key not in self.data['envs'][env].keys():
                            error = True
                            console.error("You must define the {} key inside {} environment".format(key, env))
        else:
            error = True
            console.error("Wrong version in {}".format(self.path))
        if error:
            sys.exit(1)

    def _get_environment(self):
        ret = True
        env_var = self.data['env_key']
        if not os.getenv(env_var):
            console.error('Please set {}'.format(env_var))
            ret = False
        else:
            value = os.getenv(env_var)
            environment_data = [
                data
                for data in self.data['envs']
                if self.data['envs'][data]['key_value'] == value
            ]
            if environment_data:
                self.environment = self.data['envs'][environment_data[0]]
                console.info("Using configuration for environment: {}".format(environment_data[0]))
            else:
                ret = False
                console.error("Not found configuration for {} environment. Please check {}".format(value, self.path))
        token_var = self.data['token_key']
        if not os.getenv(token_var):
            console.error("Please set your {} (https://github.com/settings/tokens)".format(token_var))
            ret = False
        else:
            self.token = os.getenv(token_var)
        return ret

    def _get_files(self):
        current_path = os.path.dirname(self.path)
        file_list = [
            os.path.join(current_path, filename)
            for filename in self.environment['files']
            if os.path.isfile(os.path.join(current_path, filename))
        ]
        return file_list

    def _check_venv(self):
        if self.environment.get('use_virtual', False):
            if hasattr(sys, 'real_prefix'):
                virtual = sys.prefix
                console.info("Running in virtual environment: {}".format(virtual))
            else:
                console.error("Virtual environment not found")
                sys.exit(1)

    def _parse_line(self, line):
        original_line = line
        line = line.strip().replace("\n", "").replace(" ", "")
        data = {
            "name": None,
            "signal": None,
            "version": None,
            "url": None,
            "head": None,
            "egg": None
        }
        # Fixed requirement
        if line.startswith("-r"):
            console.error("Option -r inside file is not allowed. Please add requirements files in pak.yml".format(original_line))
        elif not line.startswith('-e'):
            m = re.search(r"(.+)(>|=)=(\S+)", line)
            if m:
                data["name"] = m.group(1)
                data["signal"] = m.group(2)
                data["version"] = m.group(3)
            else:
                m = re.search(r"(.+)(\n|\r|$)", line)
                if m:
                    data["name"] = m.group(1)
        # edit packages
        elif line.startswith('-e'):
            # subdirectory package
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
                    data['name'] = m.group(1).split("/")[-1].replace(".git", "")
                    data['url'] = m.group(1).replace(":", "/")
                    data['head'] = m.group(2)
                    data['egg'] = m.group(3)
                else:
                    m = re.search(r"git@(.+)#egg=(.+)", line)
                    if m:
                        data['name'] = m.group(1).split("/")[-1].replace(".git", "")
                        data['url'] = m.group(1).replace(":", "/")
                        data['egg'] = m.group(3)
                    else:
                        m = re.search(r"git@(.+)", line)
                        if m:
                            data['name'] = m.group(1).split("/")[-1].replace(".git", "")
                            data['url'] = m.group(1).replace(":", "/")
        # non-fixed package
        else:
            data['name'] = line

        if not data['name']:
            console.error('Cannot parse: {}'.format(original_line))
            sys.exit(1)
        return data

    def _install_package(self, package):
        console.section("Installing {}".format(package['name']))
        console.info("Installing {}{}{}{}".format(
            "version {}= {} ".format(
                package['signal'],
                package['version'])
            if package['version'] else "",
            "at head {} ".format(package['head']) if package['head'] else "",
            'at Master ' if not package['version'] and not package['head'] else "",
            'using Token' if package['url'] else ""
        ), use_prefix=False)
        temp_dir = os.path.join(
            self.environment['clone_dir'],
            package['name']
        )
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        if package['url']:
            ret = self._run_command(
                "cd {} && git clone https://{}@{}".format(temp_dir, self.token, package['url']),
                verbose=True
            )
            if ret and package['head']:
                branchs = self._run_command(
                    'cd {}/{} && git fetch --all && git branch -a'.format(temp_dir, package['name']),
                    get_stdout=True
                )
                if branchs and package['head'] in branchs:
                    ret = self._run_command(
                        "cd {}/{} && git checkout {}".format(temp_dir, package['name'], package['head']),
                        verbose=True
                    )
                else:
                    ret = self._run_command(
                        "cd {}/{} && git reset --hard {}".format(temp_dir, package['name'], package['head']),
                        verbose=True
                    )
            if ret:
                ret = self._run_command(
                    "cd {}/{} && pip install -e .".format(temp_dir, package['name']),
                    verbose=True
                )
            if not ret:
                sys.exit(1)
        else:
            ret = self._run_command(
                "pip install {}{}{}{}{}".format(
                    package['name'],
                    '"' if package['signal'] and package['signal'] != "=" else "",
                    "{}=".format(package['signal']) if package['signal'] else "",
                    package['version'] if package['version'] else "",
                    '"' if package['signal'] and package['signal'] != "=" else "",
                ),
                verbose=True
            )
            if not ret:
                sys.exit(1)

    def run(self):

        self._load_from_config()
        self._check_config_from_version()

        if not self._get_environment():
            sys.exit(1)

        self._check_venv()

        file_list = self._get_files()
        if not file_list:
            sys.exit(0)

        package_list = []
        for file in file_list:
            console.info("Reading {}...".format(file))

            with open(file) as reqfile:
                file_list = [
                    self._parse_line(line)
                    for line in reqfile
                    if line.replace("\n", "").strip() != "" and
                    not line.replace("\n", "").strip().startswith("#")
                ]
            package_list += file_list

        for package in package_list:
            self._install_package(package)
