"""Base Outpak class."""


class BaseOutpak:
    """Base Outpak Class."""

    def __init__(self, config_path, config_data):
        """Initialize class."""
        self.path = config_path
        self.data = config_data
