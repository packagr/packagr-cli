from cleo import Command as BaseCommand
from packagr import utilities
from typing import Any, Optional, MutableMapping, Union

import os


class Command(BaseCommand):
    def check_configuration(self, hash_id: str, email: str, password: str) -> bool:
        """
        Check that a global config has been set with the `packagr configure` command
        """
        try:
            return utilities.check_configuration(hash_id, email, password)
        except AssertionError:
            self.line('<error>Invalid credentials</error>')

        return False

    def get_global_config(self) -> Optional[MutableMapping[str, Any]]:
        """
        Returns the content of the global config file

        """
        return self.get_package_config(path=os.path.expanduser('~/packagr_conf.toml'))

    def get_package_config(self, path: str = 'packagr.toml') -> Optional[MutableMapping[str, Any]]:
        config = utilities.get_package_config(path=path)

        if not config:
            self.line('<error>'
                      'Unable to perform this action because no package exists at the current location. '
                      'Run `packagr init` first'
                      '</error>')

        return config

    @staticmethod
    def write_package_content(config: dict, path: str = 'packagr.toml') -> None:
        utilities.write_package_content(config, path=path)

    def update_config(self, config, path: str = 'packagr.toml', **changes):
        for key, value in changes.items():
            config[key] = value
        self.write_package_content(config, path=path)

    def append(self,
               config: Union[dict, MutableMapping[str, Any]],
               key: str,
               value: Any,
               path: str = 'packagr.toml'
               ) -> bool:
        """
        Adds a value to an array, if it isn't already in there
        """
        existing = config.get(key, [])

        try:
            assert isinstance(existing, list)
        except AssertionError:
            self.line(f'<error>Cannot add to value {key} because it is not an array</error>')
            return False

        if value not in existing:
            existing.append(value)

        self.update_config(config=config, path=path, **{key: existing},)
        return True

    def remove(self,
               config: Union[dict, MutableMapping[str, Any]],
               key: str,
               value: Any,
               path: str = 'packagr.toml') -> bool:
        """
        Removes `n item from an array in the config
        """
        array = config.get(key, [])

        try:
            assert isinstance(array, list)

        except AssertionError:
            self.line(f'<error>Cannot remove item because the property is not an array</error>')
            return False

        try:
            array.remove(value)
        except ValueError:
            self.line(f'<error>Cannot remove item because the property {key} does not exist</error>')
            return False
        self.update_config(config=config, path=path, **{key: array})
        return True
