import os

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from outpak.config import OutpakConfig
from outpak.tests import OutpakTestBase

pip_version_result = "pip 10.0.1 from /usr/local/lib/python3.6/dist-packages/pip (python 3.6)"


class TestOutpakConfig(OutpakTestBase):

    @patch('outpak.config.OutpakConfig._load_from_yaml')
    @patch('os.path.isfile', return_value=True)
    def test_is_valid(self, *args):
        os.environ['TEST_ENV_PAK'] = 'development'
        os.environ['TEST_GIT_TOKEN_PAK'] = '1234-5678'
        os.environ['TEST_BIT_TOKEN_PAK'] = 'abcdef:1234'
        self.assertTrue(self.config.is_valid)

    def test_run_silently(self):
        self.assertFalse(self.config.run_silently)
        os.environ['OUTPAK_RUN_SILENTLY'] = 'true'
        self.assertTrue(self.config.run_silently)

    def test_default_index_url(self):
        os.environ['TEST_ENV_PAK'] = 'development'
        self.config._get_outpak_work_environment()

        # From index in default index_url in yml
        self.assertEqual(self.config.default_index_url, 'https://user:key@privatepypi.com')

        # From index in environment index_url yml
        os.environ['TEST_ENV_PAK'] = 'private'
        self.config._get_outpak_work_environment()
        self.assertEqual(self.config.default_index_url, 'https://user:key@privatepypi2.com')

        # From index in memory
        index_url = "https://user:key@mypypi.com"
        os.environ['PIP_INDEX_URL'] = index_url
        os.environ['TEST_ENV_PAK'] = 'development'
        self.config._get_outpak_work_environment()
        self.config.data.pop('index_url')
        self.assertEqual(self.config.default_index_url, index_url)

    def test_extra_indexes(self):
        os.environ['TEST_ENV_PAK'] = 'private'
        self.config._get_outpak_work_environment()
        self.assertEqual(self.config.extra_indexes, [
            'https://user:key@privatepypi3.com',
            'https://user:key@privatepypi4.com'
        ])

    def test_clone_dir(self):
        os.environ['TEST_ENV_PAK'] = 'development'
        self.config._get_outpak_work_environment()
        self.assertEqual(self.config.clone_dir, '/tmp')

    def test__load_from_yaml(self):
        os.environ['TEST_ENV_PAK'] = 'docker'
        self.config._get_outpak_work_environment()
        self.assertEqual(
            self.config.environment['key_value'],
            'docker'
        )
        instance = OutpakConfig('/tmp/do-not-exist', {})
        with self.assertRaises(SystemExit):
            instance._load_from_yaml()

    def test__validate_data_from_yaml(self):
        self.assertIsNone(self.config._validate_data_from_yaml())

    def test__get_outpak_work_environment(self):
        os.environ['TEST_ENV_PAK'] = 'development'
        self.config._get_outpak_work_environment()
        del os.environ['TEST_ENV_PAK']
        self.assertIsInstance(
            self.config.environment,
            dict
        )

    def test__get_token(self):
        os.environ['TEST_GIT_TOKEN_PAK'] = '1234-5678'
        os.environ['TEST_BIT_TOKEN_PAK'] = 'abcdef:1234'
        self.config._get_token()
        self.assertEqual(
            self.config.github_token,
            '1234-5678'
        )
        self.assertEqual(
            self.config.bitbucket_token,
            'abcdef:1234'
        )
        del os.environ['TEST_GIT_TOKEN_PAK']
        del os.environ['TEST_BIT_TOKEN_PAK']
        with self.assertRaises(SystemExit):
            self.config._get_token()

    @patch('os.path.isfile', return_value=True)
    def test__get_files(self, *args):
        os.environ['TEST_ENV_PAK'] = 'development'
        self.config._get_outpak_work_environment()
        self.config._get_files()
        self.assertEqual(len(self.config.requirement_files), 1)
        del os.environ['TEST_ENV_PAK']

    def test__check_venv(self):
        import sys
        os.environ['TEST_ENV_PAK'] = 'development'
        self.config._get_outpak_work_environment()
        del os.environ['TEST_ENV_PAK']
        is_venv = (
                hasattr(sys, 'real_prefix') or  # virtualenv
                (
                        hasattr(sys, 'base_prefix') and
                        sys.base_prefix != sys.prefix  # pyvenv
                )
        )

        if is_venv:
            self.assertIsNone(self.config._check_venv())
        else:
            with self.assertRaises(SystemExit):
                self.config._check_venv()

    @patch('buzio.console.run', return_value=pip_version_result)
    def test_get_pip_version(self, *args):
        ret = self.config.get_pip_version()
        self.assertTrue(ret, '10.0.1')
