from cleo import Command as BaseCommand
from packagr.utilities import get_package_config, write_package_content
from typing import Any
import os


class Command(BaseCommand):
    def check_configuration(self):
        """
        Check that a global config has been set with the `packagr configure` command

        TODO: implement this
        """

    def get_global_config(self):
        """
        Returns the content of the global config file

        """
        return self.get_package_config(path=os.path.expanduser('~/packagr_conf.toml'))

    def get_package_config(self, path: str = 'packagr.toml'):
        config = get_package_config(path=path)

        if not config:
            self.line('<error>'
                      'Unable to perform this action because no package exists at the current location. '
                      'Run `packagr create` first'
                      '</error>')

        return config

    @staticmethod
    def write_package_content(config: dict, path: str = 'packagr.toml') -> None:
        write_package_content(config, path=path)

    def update_config(self, config, path: str = 'packagr.toml', **changes):
        for key, value in changes.items():
            config[key] = value
        self.write_package_content(config, path=path)

    def append(self, config: dict, key: str, value: Any, path: str = 'packagr.toml') -> True:
        """
        Adds a value to an array, if it isn't already in there
        """
        existing = config.get(key, [])

        try:
            assert isinstance(existing, list)
        except AssertionError:
            self.line(f'<error>Cannot add to value {key} because it is not an array</error>')
            return

        if value not in existing:
            existing.append(value)

        self.update_config(config, **{key: existing}, path=path)
        return True

    def remove(self, config: dict, key: str, value: Any, path: str = 'packagr.toml') -> True:
        array = config.get(key, [])

        try:
            assert isinstance(array, list)

        except AssertionError:
            self.line(f'<error>Cannot remove item because the property is not an arrary</error>')
            return

        try:
            array.remove(value)
        except ValueError:
            return
        self.update_config(config, **{key: array}, path=path)
        return True
