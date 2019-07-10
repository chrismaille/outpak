"""Base Outpak class."""
import os
import re
import shutil
import sys
from typing import List

from buzio import console


class BaseOutpak:
    """Base Outpak Class."""

    version: str

    def __init__(self, config_path: str, config_data: dict) -> None:
        """Initialize class.

        :param config_path: path for pak.yml file
        :param config_data: data from pak.yml file
        """
        self.path = config_path
        self.data = config_data

    def get_files(self, file_list) -> List[str]:
        """Return existing files from list.

        Returns
        -------
            List: full path for existing files

        """
        current_path = os.path.dirname(self.path)
        file_list = [
            os.path.join(current_path, filename)
            for filename in file_list
            if os.path.isfile(os.path.join(current_path, filename))
        ]
        return file_list

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
            ret = console.run(
                "cd {} && git clone https://{}@{}".format(
                    temp_dir, self.bit_token, package['url']),
                verbose=True
            )
        else:
            ret = console.run(
                "cd {} && git clone https://{}@{}".format(
                    temp_dir, self.git_token, package['url']),
                verbose=True
            )
        if ret and package['head']:
            branchs = console.run(
                'cd {} && git fetch --all && git branch -a'.format(
                    full_package_path),
                get_stdout=True
            )
            if branchs and package['head'] in branchs:
                ret = console.run(
                    "cd {} && git checkout {}".format(
                        full_package_path, package['head']),
                    verbose=True
                )
            else:
                ret = console.run(
                    "cd {} && git reset --hard {}".format(
                        full_package_path, package['head']),
                    verbose=True
                )
        if ret:
            ret = console.run(
                "cd {} && pip install {}.".format(
                    full_package_path,
                    "{} ".format(package['option'])
                    if package['option'] else ""
                ),
                verbose=True
            )
        if not ret:
            sys.exit(1)

    def _install_with_pip(self, package):
        if package['using_line']:
            task = 'pip install "{}"'.format(package['line'])
        else:
            task = "pip install {}{}{}{}{}{}".format(
                "{} ".format(package['option']) if package['option'] else "",
                package['name'],
                '"' if package['signal'] and package['signal'] != "=" else "",
                "{}=".format(
                    package['signal']) if package['signal'] else "",
                package['version'] if package['version'] else "",
                '"' if package['signal'] and package['signal'] != "=" else "",
            )
        ret = console.run(
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
            package['signal'] if package['signal'] and package['signal'] != "=" else "",
            package['version'] if package['version'] else "latest"
        ))
        console.info("Installing {}{}".format(
            "at head {} ".format(package['head']) if package['head'] else "",
            'using Token' if package['url'] else "using pip"
        ), use_prefix=False)

        if package['url'] and not package['using_line']:
            self._install_with_url(package)
        else:
            self._install_with_pip(package)

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

    def _execute_install(self, file_list):
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
