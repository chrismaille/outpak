"""Outpak main module."""
import os
import shutil
import sys

from buzio import console
from colorama import Style, Fore

from outpak.parser import get_parser_for


class OutpakCommand:
    """OutpakCommand Class.

    Attributes
    ----------
        data (dict): data from pak.yml
        environment (dict): dictionary data from current environment
        path (string): full path for pak.yml
        token (string): git token from environment variable

    """

    def __init__(self, config):
        """Initialize class.

        Args:
            config (object): OutpakConfig instance
        """
        self.config = config
        self.parser = None

    def _create_clone_dir(self, package):
        temp_dir = os.path.join(
            self.config.clone_dir,
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
                    temp_dir, self.config.bitbucket_token, package['url']),
                verbose=not self.config.run_silently,
                silent=self.config.run_silently
            )
        else:
            ret = console.run(
                "cd {} && git clone https://{}@{}".format(
                    temp_dir, self.config.github_token, package['url']),
                verbose=not self.config.run_silently,
                silent=self.config.run_silently
            )
        if ret and package['commit']:
            branchs = console.run(
                'cd {} && git fetch --all && git branch -a'.format(
                    full_package_path),
                get_stdout=True
            )
            if branchs and package['commit'] in branchs:
                ret = console.run(
                    "cd {} && git checkout {}".format(
                        full_package_path, package['head']),
                    verbose=not self.config.run_silently,
                    silent=self.config.run_silently
                )
            else:
                ret = console.run(
                    "cd {} && git reset --hard {}".format(
                        full_package_path, package['head']),
                    verbose=not self.config.run_silently,
                    silent=self.config.run_silently
                )
        if ret:
            ret = console.run(
                "cd {clone_dir} && pip install {index}{pip_install_option}{line_option}.".format(
                    index="-i {} ".format(package['index_url']) if package['index_url'] else "",
                    clone_dir=full_package_path,
                    pip_install_option="-q " if self.config.run_silently and package['option'] is not '-q' else "",
                    line_option="{} ".format(package['option']) if package['option'] else ""
                ),
                verbose=not self.config.run_silently
            )
        if not ret:
            sys.exit(1)

    def _install_with_pip(self, package):
        if package['use_original_line']:
            task = 'pip install {index}{pip_install_option}"{requirement_line}"'.format(
                index="-i {} ".format(package['index_url']) if package['index_url'] else "",
                pip_install_option='-q ' if self.config.run_silently else '',
                requirement_line=package['original_line']
            )
        else:
            task = "pip install {index}{pip_install_option}{line_option}{name}{quotation}{signal}{quotation}{version}".format(
                index="-i {} ".format(package['index_url']) if package['index_url'] else "",
                pip_install_option='-q ' if self.config.run_silently else '',
                line_option="{} ".format(package['option']) if package['option'] else "",
                name=package['name'],
                quotation='"' if package['version'] and package['signal'] and package['signal'] != "=" else "",
                signal="{}=".format(package['signal']) if package['signal'] else "",
                version=package['version'] if package['version'] else ""
            )
        ret = console.run(
            task=task,
            verbose=not self.config.run_silently
        )
        if not ret:
            sys.exit(1)

    def install_package(self, package):
        """Install parsed package.

        Args:
            package (dict): Data parsed from package in requirements.txt
        """
        if self.config.run_silently:
            console.info("{normal}Installing {yellow}{package_line}{normal}{commit}{using}".format(
                yellow=Fore.YELLOW,
                package_line=package['line'],
                normal=Style.RESET_ALL,
                commit=" at commit {} ".format(package['commit']) if package['commit'] else "",
                using=' using Token' if package['clone_dir'] else " using Pip"
            ), use_prefix=False
            )
        else:
            console.section("Installing {}".format(
                package['line']
            ))
            console.info("Installing {}{}".format(
                "at commit {} ".format(package['commit']) if package['commit'] else "",
                'using Token' if package['url'] else "using Pip{}".format(
                    ' (silent)' if self.config.run_silently else '')
            ), use_prefix=False)

        if package['clone_dir']:
            self._install_with_url(package)
        else:
            self._install_with_pip(package)

    def execute(self):
        """Run instance."""
        if self.config.run_silently:
            console.info('Running in silent mode')

        package_list = []
        for file in self.config.requirement_files:
            if not self.config.run_silently:
                console.info("Reading {}.".format(file))

            self.parser = get_parser_for(file)
            self.parser.load_from_config(self.config)

            with open(file) as file_data:
                package_list += self.parser.get_package_list(file_data)

        for package in package_list:
            self.install_package(package)
