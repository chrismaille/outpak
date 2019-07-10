"""Unittest module.

Attributes
----------
    PAK (Str): Pak.yml model
    REQ (Str): requirements.txt model

"""
import os
import unittest
from unittest.mock import patch

import yaml
from buzio import console

from outpak.config import load_from_yaml, path_constructor, path_matcher
from outpak.main.v1 import Outpak

yaml.add_implicit_resolver('!path', path_matcher, None, yaml.SafeLoader)
yaml.add_constructor('!path', path_constructor, yaml.SafeLoader)


class TestOutpakClass(unittest.TestCase):
    """OutPak class Tests.

    Attributes
    ----------
        instance (obj): Outpak class instance
        path (str): full path for pak.yml

    """

    def setUp(self):
        """setUp."""
        super(TestOutpakClass, self).setUp()
        self.path = "/tmp/pak.yml"
        data = self.load_from_file(self.path)
        self.instance = Outpak(self.path, data)

    def tearDown(self):
        """tearDown."""
        if os.getenv('TEST_ENV_PAK'):
            del os.environ['TEST_ENV_PAK']
        if os.getenv('TEST_GIT_TOKEN_PAK'):
            del os.environ['TEST_GIT_TOKEN_PAK']
        if os.getenv('TEST_BIT_TOKEN_PAK'):
            del os.environ['TEST_BIT_TOKEN_PAK']
        if os.path.exists(self.path):
            os.remove(self.path)
        if os.path.exists('/tmp/requirements.txt'):
            os.remove('/tmp/requirements.txt')

    @staticmethod
    def load_from_file(path, version="v1"):
        current_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_path, '..', '..', 'examples', f'pak_{version}.yaml')
        with open(config_path, 'r') as file:
            pak_file = yaml.safe_load(file.read())
        with open(path, "w") as file:
            file.write(yaml.safe_dump(pak_file))
        os.remove(path)
        return pak_file

    def test_init(self):
        """test_init."""
        self.assertEqual(
            self.instance.path,
            self.path
        )

    def test_command(self):
        """test_command."""
        ret = console.run(
            task="echo hello-world",
            get_stdout=True,
            verbose=True
        )
        self.assertEqual(
            ret,
            u'hello-world\n'
        )

    def test_load_yaml(self):
        """test_load_yaml."""
        self.load_from_file(self.path)
        self.assertEqual(
            self.instance.data['github_key'],
            'TEST_GIT_TOKEN_PAK'
        )

    def test_failed_open_yml(self):
        """test_failed_open_yml."""
        with self.assertRaises(SystemExit):
            load_from_yaml('/path/do-not-exist')

    def test_validate_data_from_yaml(self):
        """test_validate_data_from_yaml."""

        self.assertIsNone(self.instance.validate_data())

    def test_get_environment_keys(self):
        """test_get_environment_keys."""

        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        del os.environ['TEST_ENV_PAK']
        self.assertIsInstance(
            self.instance.environment,
            dict
        )

    def test_get_token(self):
        """test_get_token."""

        os.environ['TEST_GIT_TOKEN_PAK'] = '1234-5678'
        os.environ['TEST_BIT_TOKEN_PAK'] = 'abcdef:1234'
        self.instance.get_token()
        self.assertEqual(
            self.instance.git_token,
            '1234-5678'
        )
        self.assertEqual(
            self.instance.bit_token,
            'abcdef:1234'
        )
        del os.environ['TEST_GIT_TOKEN_PAK']
        del os.environ['TEST_BIT_TOKEN_PAK']

    def test_token_not_found(self):
        """test_token_not_found."""

        with self.assertRaises(SystemExit):
            self.instance.get_token()

    def test_get_files(self):
        """test_get_files."""
        os.environ['TEST_ENV_PAK'] = 'development'

        self.instance.get_current_environment()
        self.assertEqual(len(self.instance.get_files(file_list=self.instance.environment['files'])), 0)
        del os.environ['TEST_ENV_PAK']

    def test_check_virtualenv(self):
        """test_check_virtualenv."""
        import sys

        os.environ['TEST_ENV_PAK'] = 'development'

        self.instance.get_current_environment()
        del os.environ['TEST_ENV_PAK']
        is_venv = (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and
                                                   sys.base_prefix != sys.prefix))

        if is_venv:
            self.assertIsNone(self.instance.check_venv())
        else:
            with self.assertRaises(SystemExit):
                self.instance.check_venv()

    def _parse_line(self, line):
        os.environ['TEST_ENV_PAK'] = 'development'

        self.instance.get_current_environment()
        del os.environ['TEST_ENV_PAK']
        return self.instance.parse_line(line)

    def test_parse_line_fixed_requirement(self):
        """test_parse_line_fixed_requirement."""
        line = "django==2.0.0"
        data = self._parse_line(line)
        self.assertEqual(
            data['name'],
            'django'
        )

    def test_parse_line_latest_requirement(self):
        """test_parse_line_latest_requirement."""
        line = "django"
        data = self._parse_line(line)
        self.assertIsNone(data['version'])

    def test_parse_line_nonsecure_requirement(self):
        """test_parse_line_nonsecure_requirement."""
        line = "-e ./package/my_package"
        data = self._parse_line(line)
        self.assertEqual(
            data['line'],
            line.replace("-e", "").strip()
        )
        self.assertTrue(data['using_line'])

    def test_parse_line_git_https(self):
        """test_parse_line_git_https."""
        line_list = [
            "-e git+https://github.com/chrismaille/outpak#egg=outpak",
            "-e git+https://github.com/chrismaille/outpak@3ecdf45#egg=outpak",
        ]
        for line in line_list:
            data = self._parse_line(line)
            self.assertEqual(
                data['url'],
                "github.com/chrismaille/outpak"
            )

    def test_parse_line_git_git(self):
        """test_parse_line_git_git."""
        line_list = [
            "-e git+git@github.com:chrismaille/outpak@1.0.0#egg=outpak",
            "-e git+git@github.com:chrismaille/outpak#egg=outpak",
        ]
        for line in line_list:
            data = self._parse_line(line)
            self.assertEqual(
                data['url'],
                "github.com/chrismaille/outpak"
            )

    def test_wrong_requirement_in_requirement(self):
        """test_wrong_requirement_in_requirement."""
        line = "-r requirements_other.txt"
        with self.assertRaises(SystemExit):
            self._parse_line(line)

    def test_create_clone_dir(self):
        """test_create_clone_dir."""
        line = "-e git+git@github.com:chrismaille/outpak@1.0.0#egg=outpak"
        package = self._parse_line(line)
        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        del os.environ['TEST_ENV_PAK']
        self.assertEqual(
            self.instance._create_clone_dir(package),
            os.path.join(self.instance.environment['clone_dir'], "outpak")
        )

    @patch("buzio.console.run",
           autospec=True, return_value="cmd")
    def test_install_package_with_url(self, *args):
        """test_install_package_with_url."""
        line = "-e git+git@github.com:chrismaille/outpak@1.0.0#egg=outpak"
        os.environ['TEST_ENV_PAK'] = 'development'
        os.environ['TEST_GIT_TOKEN_PAK'] = '12345678'
        os.environ['TEST_BIT_TOKEN_PAK'] = 'acbde:1234'

        self.instance.get_current_environment()
        self.instance.get_token()
        del os.environ['TEST_GIT_TOKEN_PAK']
        del os.environ['TEST_BIT_TOKEN_PAK']
        del os.environ['TEST_ENV_PAK']
        package = self._parse_line(line)
        self.assertIsNone(
            self.instance.install_package(package)
        )

    @patch("buzio.console.run",
           autospec=True, return_value="cmd")
    def test_install_package_with_pip(self, *args):
        """test_install_package_with_pip."""
        line = "requests[security]>=2.18.0"
        os.environ['TEST_ENV_PAK'] = 'development'

        self.instance.get_current_environment()
        del os.environ['TEST_ENV_PAK']
        package = self._parse_line(line)
        self.assertIsNone(
            self.instance.install_package(package)
        )

    @patch("buzio.console.run",
           autospec=True, return_value="cmd")
    def test_run_v1(self, *args):
        """test_run."""
        current_path = os.path.dirname(os.path.abspath(__file__))
        v1_path = os.path.join(current_path, '..', '..', 'examples', f'pak_v1.yaml')
        requirements_path = os.path.join(current_path, '..', '..', 'examples', f'requirements.txt')
        with open(v1_path, 'r') as file:
            pak_file = yaml.safe_load(file.read())
        with open(requirements_path, 'r') as file:
            requirements_file = file.read()
        with open(self.path, "w") as file:
            file.write(yaml.safe_dump(pak_file))
        with open('/tmp/requirements.txt', "w") as file:
            file.write(requirements_file)
        os.environ['TEST_ENV_PAK'] = 'development'
        os.environ['TEST_GIT_TOKEN_PAK'] = '12345abcdef'
        os.environ['TEST_BIT_TOKEN_PAK'] = "abcde:1234"
        self.assertIsNone(
            self.instance.install()
        )
