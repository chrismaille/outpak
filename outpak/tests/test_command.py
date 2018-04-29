import os
import shutil

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from outpak.command import OutpakCommand
from outpak.parser import PipParser
from outpak.tests import OutpakTestBase, REQ


class TestOutpakCommand(OutpakTestBase):

    def setUp(self):
        super(TestOutpakCommand, self).setUp()
        os.environ['TEST_ENV_PAK'] = 'development'
        os.environ['TEST_GIT_TOKEN_PAK'] = '1234-5678'
        os.environ['TEST_BIT_TOKEN_PAK'] = 'abcdef:1234'
        self._load_from_file()
        self.config._get_outpak_work_environment()
        self.command = OutpakCommand(self.config)

    def test__create_clone_dir(self):
        package = {'name': 'outpak'}
        temp_dir = self.command._create_clone_dir(package)
        shutil.rmtree(temp_dir)
        self.assertEqual(
            temp_dir,
            os.path.join(self.config.environment['clone_dir'], "outpak")
        )

    @patch('buzio.console.run', return_value="data")
    def test__install_with_url(self, *args):
        line = "-e git+https://github.com/chrismaille/outpak@3ecdf45#egg=outpak"
        parser = PipParser()
        parser.load_from_config(self.config)
        package = parser.parse_line(line)
        self.assertEqual(package['url'], 'github.com/chrismaille/outpak')
        self.assertFalse(package['use_original_line'])
        self.assertIsNone(self.command._install_with_url(package))

    @patch('buzio.console.run', return_value="data")
    def test__install_with_pip(self, *args):
        line = "requests[security]>=2.18.0"
        parser = PipParser()
        parser.load_from_config(self.config)
        package = parser.parse_line(line)
        self.assertIsNone(package['url'])
        self.assertIsNone(self.command._install_with_pip(package))

    def test_install_package(self):
        self.fail()

    @patch('outpak.command.OutpakCommand.install_package')
    def test_execute(self, *args):
        with open('/tmp/requirements.txt', "w") as file:
            file.write(REQ)
        self.command.config._get_files()
        self.assertIsNone(
            self.command.execute()
        )

