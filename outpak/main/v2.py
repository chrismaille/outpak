"""Outpak version 1."""
from typing import Any, Dict, List, Optional

from buzio import console

from outpak.main.base import BaseOutpak


class OutpakConfig:
    """Outpak Config data."""

    valid_sources = ['story', 'commit']
    valid_labels = ['type', 'label', 'body', 'title']

    def __init__(self, data: dict):
        """Initialize class.

        :param data: data parsed from yaml.
        """
        self.data = data

    @property
    def commands(self) -> Dict[str, dict]:
        """Return top key 'commands' from yaml.

        :return: List
        """
        return self.data.get('commands', {})

    @property
    def providers(self) -> Dict[str, dict]:
        """Return top key 'providers' from yaml.

        :return: Dict
        """
        return self.data.get('providers', {})

    def validate(self) -> bool:
        """Validate data from yaml.

        :return: Bool
        """
        found_errors = False
        # Check each command configuration
        for command in self.commands:
            command_data: Dict[Any, Any] = self.commands.get(command)  # type: ignore
            if command_data.get('provider'):
                if not self.providers.get(command_data.get('provider'), {}).get('authorization_token'):  # type: ignore
                    console.error(f"[{command}] Provider {command_data.get('provider')} was defined in command"
                                  f" {command}, but no authorization token was found")
                    found_errors = True

            # Missing files
            if command in ['install', 'changelog'] and not command_data.get('files'):
                console.error(f"[{command}]You must inform file list for this command.")
                found_errors = True

            # version command
            if command == "version":
                if not command_data.get('source') or command_data.get('source') not in self.valid_sources:
                    console.error(f"[{command}] You must provide a source "
                                  f"for versioning rules: {','.join(self.valid_sources)}")
                    found_errors = True
                if command_data.get('source') == 'story' and not command_data.get('provider'):
                    console.error(f"[{command}] You must provide a provider for story based versioning")
                    found_errors = True
                if not command_data.get('rules', {}).get('minor') and not command_data.get('rules', {}).get('major'):
                    console.error(
                        f"[{command}] You must define at least one rule for versioning (patch, minor or major)")
                    found_errors = True
                for rule in command_data.get('rules', []):
                    for condition in command_data.get('rules')[rule]:  # type: ignore
                        if condition.get('label') not in self.valid_labels:
                            console.error(f"[{command}] Label for condition {condition} not exists or invalid. "
                                          f"Valid ones are: {','.join(self.valid_labels)}")
                            found_errors = True
                        if not condition.get('value'):
                            console.error(f"[{command}] Label for condition {condition} must have a value.")
                            found_errors = True
        return not found_errors

    def get_files_for(self, command) -> Optional[List[str]]:
        """Return file list for command.

        :param command: command will be processed
        :return: List
        """
        return self.data.get('commands', {}).get(command, {}).get('files')


class Outpak(BaseOutpak):
    """Outpak class v2."""

    version = "2"

    def __init__(self, config_path, config_data):
        """Initialize class.

        :param config_path: path for yaml file.
        :param config_data: data parsed from yaml file.
        """
        super(Outpak, self).__init__(config_path, config_data)
        self.config = OutpakConfig(config_data)

    def validate_data(self) -> bool:
        """Validate data from yaml.

        :return: Boolean
        """
        return self.config.validate()

    def install(self) -> None:
        """Install command main logic.

        :return: None
        """
        file_list = self.get_files(file_list=self.config.get_files_for('install'))
        self._execute_install(file_list)
