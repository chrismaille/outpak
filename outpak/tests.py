"""Unittest module.

Attributes
----------
    PAK (Str): Pak.yml model
    REQ (Str): requirements.txt model

"""
import unittest
import os
from outpak.main import Outpak

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

PAK = """
version: "1"
github_key: TEST_GIT_TOKEN_PAK
bitbucket_key: TEST_BIT_TOKEN_PAK
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

REQ = """
# This is a comment

-r requirements_test.txt
SomeProject
SomeProject == 1.3
SomeProject >=1.2,<.2.0
SomeProject[foo, bar]
SomeProject~=1.4.2
SomeProject ==5.4 ; python_version < '2.7'
SomeProject; sys_platform == 'win32'
SomeProject[foo]>=2.18.1  # another comment

FooProject >= 1.2 --global-option="--no-user-cfg" \
                  --install-option="--prefix='/usr/local'" \
                  --install-option="--no-compile"

https://git.myproject.org/MyProject#egg=MyProject
https://git.myproject.org/MyProject@commit123#egg=MyProject

git://git.myproject.org/MyProject#egg=MyProject
git+http://git.myproject.org/MyProject#egg=MyProject
git+https://git.myproject.org/MyProject#egg=MyProject
git+ssh://git.myproject.org/MyProject#egg=MyProject
git+git://git.myproject.org/MyProject#egg=MyProject
git+file://git.myproject.org/MyProject#egg=MyProject
-e git+git@git.myproject.org:MyProject#egg=MyProject

git://git.myproject.org/MyProject.git@master#egg=MyProject
git://git.myproject.org/MyProject.git@v1.0#egg=MyProject
git://git.myproject.org/MyProject.git@da39a3ee5e6b4b0d3255bfef95601890afd80709#egg=MyProject

hg+http://hg.myproject.org/MyProject#egg=MyProject
hg+https://hg.myproject.org/MyProject#egg=MyProject
hg+ssh://hg.myproject.org/MyProject#egg=MyProject

hg+http://hg.myproject.org/MyProject@da39a3ee5e6b#egg=MyProject
hg+http://hg.myproject.org/MyProject@2019#egg=MyProject
hg+http://hg.myproject.org/MyProject@v1.0#egg=MyProject
hg+http://hg.myproject.org/MyProject@special_feature#egg=MyProject

svn+svn://svn.myproject.org/svn/MyProject#egg=MyProject
svn+http://svn.myproject.org/svn/MyProject/trunk@2019#egg=MyProject

bzr+http://bzr.myproject.org/MyProject/trunk#egg=MyProject
bzr+sftp://user@myproject.org/MyProject/trunk#egg=MyProject
bzr+ssh://user@myproject.org/MyProject/trunk#egg=MyProject
bzr+ftp://user@myproject.org/MyProject/trunk#egg=MyProject
bzr+lp:MyProject#egg=MyProject
bzr+https://bzr.myproject.org/MyProject/trunk@2019#egg=MyProject
bzr+http://bzr.myproject.org/MyProject/trunk@v1.0#egg=MyProject

-e ./packages/my_package
"""


class TestOutpakRunModule(unittest.TestCase):
    """Run module tests."""

    def get_pak_yml_path_default(self):
        """test_get_path."""
        from outpak.run import get_pak_yml_path
        self.assertEqual(
            get_pak_yml_path(),
            os.path.join(os.getcwd(), 'pak.yml')
        )

    def get_pak_yml_path_from_env(self):
        """test_get_from_env."""
        from outpak.run import get_pak_yml_path
        os.environ['OUTPAK_FILE'] = '/tmp/pak.yml'
        ret = get_pak_yml_path()
        del os.environ['OUTPAK_FILE']
        self.assertEqual(
            ret,
            '/tmp/pak.yml'
        )

    @patch("outpak.run.Outpak", autospec=True)
    @patch(
        "outpak.run.argparse.ArgumentParser",
        autospec=True
    )
    def test_run(self, *args):
        """test_run."""
        from outpak.run import run
        self.assertIsNone(run())


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
        self.instance = Outpak(self.path)

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

    def _load_from_file(self):
        with open(self.path, "w") as file:
            file.write(PAK)
        self.instance.load_from_yaml()
        os.remove(self.path)

    def test_init(self):
        """test_init."""
        self.assertEqual(
            self.instance.path,
            self.path
        )

    def test_command(self):
        """test_command."""
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
        """test_load_yaml."""
        self._load_from_file()
        self.assertEqual(
            self.instance.data['github_key'],
            'TEST_GIT_TOKEN_PAK'
        )

    def test_failed_open_yml(self):
        """test_failed_open_yml."""
        instance = Outpak('/tmp/do-not-exist')
        with self.assertRaises(SystemExit):
            instance.load_from_yaml()

    def test_validate_data_from_yaml(self):
        """test_validate_data_from_yaml."""
        self._load_from_file()
        self.assertIsNone(self.instance.validate_data_from_yaml())

    def test_failed_version_check_from_yml(self):
        """test_failed_version_check_from_yml."""
        self._load_from_file()
        self.instance.data['version'] = "x"
        with self.assertRaises(SystemExit):
            self.instance.validate_data_from_yaml()

    def test_get_environment_keys(self):
        """test_get_environment_keys."""
        self._load_from_file()
        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        del os.environ['TEST_ENV_PAK']
        self.assertIsInstance(
            self.instance.environment,
            dict
        )

    def test_get_token(self):
        """test_get_token."""
        self._load_from_file()
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
        self._load_from_file()
        with self.assertRaises(SystemExit):
            self.instance.get_token()

    def test_get_files(self):
        """test_get_files."""
        self._load_from_file()
        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        self.assertEqual(len(self.instance.get_files()), 0)
        del os.environ['TEST_ENV_PAK']

    def test_check_virtualenv(self):
        """test_check_virtualenv."""
        import sys

        self._load_from_file()
        os.environ['TEST_ENV_PAK'] = 'development'
        self.instance.get_current_environment()
        del os.environ['TEST_ENV_PAK']
        is_venv = (
            hasattr(sys, 'real_prefix') or  # virtualenv
            (
                hasattr(sys, 'base_prefix') and
                sys.base_prefix != sys.prefix  # pyvenv
            )
        )

        if is_venv:
            self.assertIsNone(self.instance.check_venv())
        else:
            with self.assertRaises(SystemExit):
                self.instance.check_venv()

    def _parse_line(self, line):
        self._load_from_file()
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

    @patch("outpak.main.subprocess.check_output",
           autospec=True, return_value="cmd")
    @patch("outpak.main.subprocess.call", autospec=True, return_value=0)
    def test_install_package_with_url(self, *args):
        """test_install_package_with_url."""
        line = "-e git+git@github.com:chrismaille/outpak@1.0.0#egg=outpak"
        os.environ['TEST_ENV_PAK'] = 'development'
        os.environ['TEST_GIT_TOKEN_PAK'] = '12345678'
        os.environ['TEST_BIT_TOKEN_PAK'] = 'acbde:1234'
        self._load_from_file()
        self.instance.get_current_environment()
        self.instance.get_token()
        del os.environ['TEST_GIT_TOKEN_PAK']
        del os.environ['TEST_BIT_TOKEN_PAK']
        del os.environ['TEST_ENV_PAK']
        package = self._parse_line(line)
        self.assertIsNone(
            self.instance.install_package(package)
        )

    @patch("outpak.main.subprocess.check_output",
           autospec=True, return_value="cmd")
    @patch("outpak.main.subprocess.call", autospec=True, return_value=0)
    def test_install_package_with_pip(self, *args):
        """test_install_package_with_pip."""
        line = "requests[security]>=2.18.0"
        os.environ['TEST_ENV_PAK'] = 'development'
        self._load_from_file()
        self.instance.get_current_environment()
        del os.environ['TEST_ENV_PAK']
        package = self._parse_line(line)
        self.assertIsNone(
            self.instance.install_package(package)
        )

    def test_install_with_pip(self):
        """test_install_with_pip."""
        def assert_command(package, task, pip_quiet=False):
            pak = Outpak(self.path, pip_quiet=pip_quiet)
            pak._run_command = MagicMock()
            pak._install_with_pip(package)
            pak._run_command.assert_called_once_with(
                task=task,
                verbose=True
            )

        assert_command({
                'name': 'foo',
                'option': '-opt',
                'version': '1.2.3',
                'signal': '>',
                'using_line': False
            },
            'pip install -opt foo">=1.2.3"'
        )
        assert_command({
                'name': 'foo',
                'option': None,
                'version': '1.2.3',
                'signal': '=',
                'using_line': False
            },
            'pip install foo==1.2.3'
        )
        assert_command({
                'name': 'foo',
                'option': '-e',
                'version': '1.2.3',
                'signal': '<',
                'using_line': False
            },
            'pip install -q -e foo"<=1.2.3"',
            pip_quiet=True
        )
        assert_command({
                'line': 'foo==6.6.6',
                'option': None,
                'using_line': True
            },
            'pip install -q "foo==6.6.6"',
            pip_quiet=True
        )

    @patch("outpak.main.subprocess.check_output",
           autospec=True, return_value="cmd")
    @patch("outpak.main.subprocess.call", autospec=True, return_value=0)
    def test_run(self, *args):
        """test_run."""
        with open(self.path, "w") as file:
            file.write(PAK)
        with open('/tmp/requirements.txt', "w") as file:
            file.write(REQ)
        os.environ['TEST_ENV_PAK'] = 'development'
        os.environ['TEST_GIT_TOKEN_PAK'] = '12345abcdef'
        os.environ['TEST_BIT_TOKEN_PAK'] = "abcde:1234"
        self.assertIsNone(
            self.instance.run()
        )
