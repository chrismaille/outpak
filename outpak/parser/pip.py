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

        For every line with cvs+protocol Outpak will clone the repository first
        then run pip install command in cloned directory

        For every other non-comment line, run pip install with line
        """
        original_line = line
        line = line.split(" #")[0]  # removing comments (need space)
        line = line.strip().replace("\n", "")
        data = {
            "index_url": None,
            "extra_indexes": [],
            "line": line,
            "clone_url": None,
            "commit": None
        }
        # Line is -r or -c
        if line.startswith("-r") or line.startswith('-c '):
            console.error("Line {} not allowed. Please add additional files in pak.yml".format(line))
            sys.exit(1)

        # Line starts with '-i' or '--index-url'
        if line.startswith('-i') or line.startswith('--index-url'):
            m = re.search(r"-+\w+\s+(\S+)", line)
            if m:
                self.current_index = m.group(1)
                return
            else:
                console.error('Cannot parse: {}'.format(line))
                sys.exit(1)

        # Line starts with "--extra-index-url"
        if line.startswith('--extra-index-url'):
            m = re.search(r"-+\w+\s+(\S+)", line)
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

        # Find lines which need cloning
        # TODO: Parse commits from URL
        if "://" in line and "$" not in line:
            url = line.split('://')[1].replace(":", "/").split("#")[0]
            if ";" in url:
                url = url.split(";")[0].rstrip()
            data['clone_url'] = url
        elif "+" in line and "@" in line and "$" not in line:
            url = line.split("@")[1].replace(":", "/").split("#")[0]
            if ";" in url:
                url = url.split(";")[0].rstrip()
            data['clone_url'] = url.replace("https://", "").replace("http://", "")

        return data
