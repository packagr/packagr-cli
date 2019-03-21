from cleo import Command as BaseCommand
from packagr import utilities
from typing import Any, Optional, MutableMapping, Union, List
from packagr.objects import Package, Token, User
import os


class Command(BaseCommand):
    @property
    def headers(self):
        access_token = self.get_access_token()
        return {
            'Authorization': f'JWT {access_token}'
        }

    def get_access_token(self):
        token = utilities.get_access_token()
        if token:
            return token
        else:
            self.line('<error>Unable to get login token from Packagr</error>')
            return None

    def get_packages(self) -> Optional[List[Package]]:
        packages = utilities.get_packages(headers=self.headers)

        if not packages:
            self.line('<error>Invalid status code</error>')

        return packages

    def get_tokens(self) -> Optional[List[Token]]:
        tokens = utilities.get_tokens(headers=self.headers)

        if not tokens:
            self.line('<error>Invalid status code</error>')

        return tokens

    def get_users(self) -> Optional[List[User]]:
        users = utilities.get_users(headers=self.headers)

        if not users:
            self.line('<error>Invalid status code</error>')

        return users

    def retrieve_package(self, name: str) -> Optional[Package]:
        packages = self.get_packages()

        if packages:
            matching = list(filter(lambda x: x.name == name, packages))
            if matching:
                return matching[0]

        self.line('<error>Cannot find a package with that name</error>')
        return None

    def retrieve_token(self, package: Package, user: User) -> Optional[Token]:
        tokens = self.get_tokens()

        if tokens:
            matching = list(filter(lambda x: x.package == package.uuid and x.user == user.hash_id, tokens))

            if matching:
                return matching[0]

        self.line('<error>Cannot find an access token for this user/package</error>')
        return None

    def retrieve_user(self, email: str) -> Optional[User]:
        users = self.get_users()

        if users:
            matching = list(filter(lambda x: x.email == email, users))
            if matching:
                return matching[0]

        self.line('<error>Cannot find a user with that email address</error>')
        return None

    def create_access_token(self, package: Package, user: User, write_access: bool = False) -> bool:
        """
        Create an access token for a specific package/user combination
        """
        ok, error = utilities.create_access_token(self.headers, package, user, write_access)

        if not ok:
            self.line(f'<error>Could not create access token due to {error} error</error>')

        return ok

    def delete_access_token(self, token: Token) -> Optional[bool]:
        deleted, error = utilities.delete_access_token(token, self.headers)

        if not deleted:
            self.line(f'<error>{error}</error>')

        return deleted

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
