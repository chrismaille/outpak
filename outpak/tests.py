import unittest
import os
from outpak.main import Outpak

PAK = """
version: "1"
token_key: TEST_TOKEN_PAK
env_key: TEST_ENV_PAK
envs:
  dev:
    key_value: development
    use_virtual: True
    clone_dir: /tmp/core
    files:
      - requirements.txt
  docker:
    key_value: docker
    clone_dir: /opt/src
    files:
      - requirements.txt
"""


class TestOutpak(unittest.TestCase):

    def setUp(self):
        super(TestOutpak, self).setUp()
        self.path = "/tmp/pak.yml"
        self.instance = Outpak(self.path)

    def _load_from_file(self):
        with open(self.path, "w") as file:
            file.write(PAK)
        self.instance.load_from_yaml()
        os.remove(self.path)

    def test_init(self):
        self.assertEqual(
            self.instance.path,
            self.path
        )

    def test_command(self):
        ret = self.instance._run_command(
            task="echo hello-world",
            get_stdout=True,
            verbose=True
        )
        self.assertEqual(
            ret,
            u'hello-world\n'
        )

    def test_load_yaml(self):
        self._load_from_file()
        self.assertEqual(
            self.instance.data['token_key'],
            'TEST_TOKEN_PAK'
        )

    def test_failed_open_yml(self):
        instance = Outpak('/tmp/do-not-exist')
        with self.assertRaises(SystemExit):
            instance.load_from_yaml()

    def test_validate_data_from_yaml(self):
        self._load_from_file()
        self.assertIsNone(self.instance.validate_data_from_yaml())

    def test_failed_version_check_from_yml(self):
        self._load_from_file()
        self.instance.data['version'] = "x"
        with self.assertRaises(SystemExit):
            self.instance.validate_data_from_yaml()

    def test_get_environment_keys(self):
        self._load_from_file()
        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        self.assertIsInstance(
            self.instance.environment,
            dict
        )
        del os.environ['TEST_ENV_PAK']

    def test_get_token(self):
        self._load_from_file()
        os.environ['TEST_TOKEN_PAK'] = '1234-5678'
        self.instance.get_token()
        self.assertEqual(
            self.instance.token,
            '1234-5678'
        )
        del os.environ['TEST_TOKEN_PAK']

    def test_token_not_found(self):
        self._load_from_file()
        with self.assertRaises(SystemExit):
            self.instance.get_token()

    def test_get_files(self):
        self._load_from_file()
        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        self.assertEqual(len(self.instance.get_files()), 0)
        del os.environ['TEST_ENV_PAK']

    def test_check_virtualenv(self):
        import sys 
        
        self._load_from_file()
        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        if hasattr(sys, 'real_prefix'):
            self.assertIsNone(self.instance.check_venv())
        else:
            with self.assertRaises(SystemExit):
                self.instance.check_venv()

    def _parse_line(self, line):
        self._load_from_file()
        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        return self.instance.parse_line(line)

    def test_parse_line_fixed_requirement(self):
        line = "django==2.0.0"
        data = self._parse_line(line)
        self.assertEqual(
            data['name'],
            'django'
        )

    def test_parse_line_latest_requirement(self):
        line = "django"
        data = self._parse_line(line)
        self.assertIsNone(data['version'])

    def test_parse_line_nonsecure_requirement(self):
        line = "-e ./package/my_package"
        data = self._parse_line(line)
        self.assertEqual(
            data['name'],
            line.replace(" ", "")
        )

    def test_parse_line_git_https(self):
        line = "-e git+https://github.com/chrismaille/outpak#egg=outpak"
        data = self._parse_line(line)
        self.assertEqual(
            data['url'],
            "github.com/chrismaille/outpak"
        )

    def test_parse_line_git_git(self):
        line = "-e git+git@github.com:chrismaille/outpak@1.0.0#egg=outpak"
        data = self._parse_line(line)
        self.assertEqual(
            data['url'],
            "github.com/chrismaille/outpak"
        )

    def test_fail_parse_line(self):
        line = "-k xxxxx"
        with self.assertRaises(SystemExit):
            self._parse_line(line)

    def test_fail_requirement_in_requirement(self):
        line = "-r requirements_other.txt"
        with self.assertRaises(SystemExit):
            self._parse_line(line)