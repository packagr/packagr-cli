from commands.base import Command
import os
import toml


class PackagrCLIException(Exception):
    pass


class ConfigureClient(Command):
    """
    Configure the CLI for your Packagr account

    configure
        {hash-id? : TYour Packagr account hash ID}
        {email? : Your packagr email address}
        {password? : Your packagr password}

    """

    def handle(self):
        """
        Creates a packagr config file at the root directory

        TODO: Need to update this to actually validate the hash_id and api_access_key before setting these values
        """

        hash_id: str = self.argument('hash-id')
        email: str = self.argument('email')
        password: str = self.argument('password')

        config_path = os.path.expanduser('~')

        content = {
            # 'url': f'https://api.packagr.app/{hash_id}/',
            'url': f'http://localhost:8000/{hash_id}/',
            'email': email,
            'password': password
        }

        with open(os.path.join(config_path, 'packagr_conf.toml'), 'w') as f:
            f.write(toml.dumps(content))

        self.line('Successfully updated config file')


class SetValue(Command):
    """
    Adds a configuration variable to your project config

    set
        {key? : The property to update}
        {value? : The new value}
    """
    def handle(self):
        key, value = self.argument('key'), self.argument('value')

        config = self.get_package_config()
        if config:
            try:
                assert not isinstance(config.get(key), list)
            except AssertionError:
                new_type = type(value)
                if not self.confirm(f'You are about to replace an array with a {new_type.__name__}. Continue?', False,
                                    '(?i)^(y|j)'):
                    return

            self.update_config(config, **{key: value})
            self.line(f'Successfully added key "{key}" with value "{value}"')


class AddValue(Command):
    """
    Appends a value to an existing array in the config

    add
        {key? : The property to update}
        {value? : The new value}
    """
    def handle(self):
        key = self.argument('key')
        value = self.argument('value')

        config = self.get_package_config()
        if not config:
            return

        if self.append(config, key, value):
            self.line(f'Successfully added key "{key}" with value "{value}"')


class InstallCommand(Command):
    """
    Installs a package and updates the config

    install
        {name? : The name of the package to install}
    """

    def handle(self):
        """
        1. Looks for the given package on Packagr repo
        2. If not found, looks for it on PYPI
        3. Installs it
        4. Adds to config

        TODO: Implement steps 1-3
        """
        config = self.get_package_config()
        if config:
            self.append(config, 'install_requires', self.argument('name'))

            self.line('added package to config')


class BumpVersion(Command):
    """
    Increases the version number of a package, e.g. 1.0.0 > 1.0.1, assuming that semver is used

    bump
        {version? : The new version number}
        {--a|major : Bumps the major version e.g. 1.0.0 > 2.0.0}
        {--i|minor : Bumps the minor version e.g. 1.0.0 > 1.1.0}
    """

    def handle(self):
        config = self.get_package_config()
        if not config:
            return

        version = config.get('version', '0.1.0')
        version_opt = self.argument('version')
        major_opt, minor_opt = self.option('major'), self.option('minor')

        if version_opt:
            if major_opt or minor_opt:
                self.line('<error>'
                          'Cannot use the version argument with either the --minor or --major arguments'
                          '</error>')
                return

            new_version = version_opt

        else:
            try:
                major, minor, bugfix = version.split('.')
            except ValueError:
                self.line('<error>Cannot automatically bump version because this package does not appear to '
                          'use Semver. Use `packagr bump <version>` instead</error>')
                return

            if major_opt or minor_opt:
                if major_opt:
                    major = int(major) + 1

                if minor_opt:
                    minor = int(minor) + 1

            elif not version_opt:
                bugfix = int(bugfix) + 1

            new_version = f'{major}.{minor}.{bugfix}'

        self.update_config(config, version=new_version)
        self.line(f'Updated version to {new_version}')


class CreatePackage(Command):
    """
    Creates a new Packagr config file

    init
        {name? : The name of the package - default to the current folder name if not provided}
        {--o|overwrite : Overwrite existing without prompt}

    """

    def handle(self):
        """
        Creates a file called `packagr.toml` in the current directory

        Checks if file exists first, prompts to replace

        """
        name = self.argument('name')
        if not name:
            name = os.path.split(os.getcwd())[-1]
        overwrite = self.option('overwrite')

        template = {
            'name': name,
            'version': '0.1.0',
            'packages': [name]
        }
        if not os.path.exists(name):
            os.makedirs(name)

        if os.path.exists('packagr.toml') and not overwrite:
            if not self.confirm('A package already exists at this location. Overwrite?', False, '(?i)^(y|j)'):
                return

        self.write_package_content(template)
        response = 'Created config file `packagr.toml`'

        self.line(response)
