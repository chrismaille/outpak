import re
import sys

from buzio import console


class PipParser:

    def __init__(self):
        self.current_index = None
        self.extra_indexes = []
        self.run_silently = False

    def load_from_config(self, config):
        self.current_index = config.default_index_url
        self.extra_indexes = config.extra_indexes
        self.run_silently = config.run_silently

    def get_package_list(self, data_from_file):
        file_list = []
        for line in data_from_file:
            line_to_read = ""
            if line.strip().startswith("#") or \
                    line.strip().startswith("-r") or \
                    line.strip().startswith("-c") or \
                    line.strip().replace("\n", "") == "":
                continue
            if "\\" in line:
                line_to_read += "".join(
                    line.strip().split("\\")[0]
                )
                continue
            elif not line_to_read:
                line_to_read = line
            line_to_read = line_to_read.replace("\n", "").strip()
            if line_to_read != "":
                file_list.append(self.parse_line(line_to_read))

        return file_list

    def parse_line(self, line):
        """Parse requirements line engine.

        Read the line from requirements.txt, ignoring # commments.

        Stop if "-r" or "-c" in requirement is found.
        Change index if "-i" in requirement is found
        Change extra indexes if "--extra-index" in requirement is found
        Do not use extra indexes if "--no-index" in requirement is found

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
            "use_original_line": False,
            "option": "",
            "index_url": None,
            "extra_indexes": [],
            "original_line": original_line
        }
        # Line is -r or -c
        if line.startswith("-r") or line.startswith('-c '):
            console.error("Line {} not allowed. Please add additional files in pak.yml".format(line))
            sys.exit(1)

        # Line starts with '-i' or '--index-url'
        if line.startswith('-i') or line.startswith('--index-url'):
            m = re.search(r"\-+\w+\s+(\S+)", line)
            if m:
                self.current_index = m.group(1)
                return
            else:
                console.error('Cannot parse: {}'.format(line))
                sys.exit(1)

        # Line starts with "--extra-index-url"
        if line.startswith('--extra-index-url'):
            m = re.search(r"\-+\w+\s+(\S+)", line)
            if m:
                self.extra_indexes.append = m.group(1)
                return
            else:
                console.error('Cannot parse: {}'.format(line))
                sys.exit(1)

        # Line starts with "--no-index"
        if line.startswith('--no-index'):
            self.current_index = None
            self.extra_indexes = []
            return

        data['index_url'] = self.current_index
        data['extra_indexes'] = self.extra_indexes

        # Find other options:
        if line.startswith('-e'):
            data['option'] = "-e"

        if line.startswith('-f') or line.startswith('--find-links'):
            data['option'] = "-f" if line.startswith('-f') else '--find-links'

        if line.startswith('--no-binary'):
            data['option'] = "--no-binary"

        if line.startswith('--no-binary'):
            data['option'] = "--no-binary"

        if line.startswith('--only-binary'):
            data['option'] = "--only-binary"

        if line.startswith('--require-hashes'):
            data['option'] = "--require-hashes"

        line = line.replace(data['option'], "")

        # SomeProject ==5.4 ; python_version < '2.7'
        if ";" in line:
            data['name'] = line.split(";")[0]
            data['use_original_line'] = True
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
            data['use_original_line'] = True
            return data

        # hg+http://hg.myproject.org/MyProject#egg=MyProject
        # svn+http://svn.myproject.org/svn/MyProject/trunk@2019#egg=MyProject
        # bzr+lp:MyProject#egg=MyProject
        if "hg+" in line or "svn+" in line or "bzr+" in line:
            data['name'] = line
            data['line'] = line
            data['use_original_line'] = True
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
            data['use_original_line'] = True
            data['name'] = data['line'].split("@")[0].split("/")[-1]
            return data

        console.error('Cannot parse: {}'.format(original_line))
        sys.exit(1)
