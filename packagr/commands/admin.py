from packagr.commands.base import Command
import os
import toml
import subprocess


class ConfigureClient(Command):
    """
    Configure the CLI for your Packagr account

    configure
        {hash-id : TYour Packagr account hash ID}
        {email : Your packagr email address}
        {password : Your packagr password}

    """

    def handle(self) -> None:
        """
        Creates a packagr config file at the root directory
        """

        hash_id: str = self.argument('hash-id')
        email: str = self.argument('email')
        password: str = self.argument('password')

        if self.check_configuration(hash_id, email, password):
            config_path = os.path.expanduser('~')

            content = {
                'url': f'https://api.packagr.app/{hash_id}/',
                'email': email,
                'hash-id': hash_id,
                'password': password
            }

            with open(os.path.join(config_path, 'packagr_conf.toml'), 'w') as f:
                f.write(toml.dumps(content))

            self.line('<info>Successfully updated config file</info>')


class SetValue(Command):
    """
    Adds a configuration variable to your project config

    set
        {key? : The property to update}
        {value? : The new value}
    """
    def handle(self) -> None:
        key, value = self.argument('key'), self.argument('value')

        config = self.get_package_config()
        if config:
            try:
                assert not isinstance(config.get(key), list)
            except AssertionError:
                new_type = type(value)
                if not self.confirm(f'You are about to replace an array with a {new_type.__name__}. Continue?', False,
                                    '(?i)^(y|j)'):
                    self.line('<error>Operation cancelled by user</error>')
                    return

            self.update_config(config, **{key: value})
            self.line(f'Successfully added key "{key}" with value "{value}"')
        else:
            self.line('<error>No package found - Run `packagr init` first</error>')


class AddValue(Command):
    """
    Appends a value to an existing array in the config

    add
        {key? : The property to update}
        {value? : The new value}
    """
    def handle(self) -> None:
        key = self.argument('key')
        value = self.argument('value')

        config = self.get_package_config()
        if config:
            if self.append(config, key, value):
                self.line(f'Successfully added key "{key}" with value "{value}"')

        else:
            self.line('<error>No package found - Run `packagr init` first</error>')


class RemoveValue(Command):
    """
    Appends a value to an existing array in the config

    remove
        {key? : The property to update}
        {value? : The value to remove}
    """
    def handle(self) -> None:
        key = self.argument('key')
        value = self.argument('value')

        config = self.get_package_config()
        if config:
            if self.remove(config, key, value):
                self.line(f'Successfully removed value {value} from array "{key}"')

        else:
            self.line('<error>No package found - Run `packagr init` first</error>')

class InstallCommand(Command):
    """
    Installs a package and updates the config

    install
        {packages* : The packages to install}
        {--i|ignore-errors : Continue to the next file even if errors are encountered}
    """

    def handle(self) -> None:
        packages = self.argument('packages')
        ignore_errors = self.option('ignore-errors')

        config = self.get_global_config()

        if config:
            if self.check_configuration(config['hash-id'], config['email'], config['password']):
                url = f'https://{config["email"]}:{config["password"]}@api.packagr.app/{config["hash-id"]}/'

                for package in packages:
                    status = subprocess.call(['pip', 'install', package, '--extra-index-url', url, '-q'])

                    if status == 0:
                        config = self.get_package_config()
                        if config:
                            self.append(config, 'install_requires', package)

                            self.line(f'<info>Installed package {package} and added it to the config</info>')
                    else:
                        self.line(f'<error>Error installing package {package}.</error>')
                        if not ignore_errors:
                            self.line('<error>Stopping process</error>')
                            return

            else:
                self.line('<error>Packagr credentials are invalid</error>')

        else:
            self.line('<error>Global config not found</error>')


class UninstallCommand(Command):
    """
    Uninstalls a package and removes it from the config

    uninstall
        {packages* : The packages to uninstall}
        {--i|ignore-errors : Continue to the next file even if errors are encountered}
        {--y|skip-prompts : Skip uninstall prompts}
    """
    def handle(self) -> None:
        packages = self.argument('packages')

        ignore_errors = self.option('ignore-errors')
        skip_prompts = self.option('skip-prompts')

        config = self.get_package_config()

        if config:
            for package in packages:
                commands = ['pip', 'uninstall', package,]
                if skip_prompts:
                    commands.append('-y')
                status = subprocess.call(commands)
                if status == 0:
                    self.remove(config, 'install_requires', package)
                    self.line(f'<info>Successfully uninstalled {package}</info>')

                else:
                    self.line(f'<error>Error uninstalling package {package}.</error>')
                    if not ignore_errors:
                        self.line('<error>Stopping process</error>')
                        return
        else:
            self.line('<error>No package found - Run `packagr init` first</error>')


class BumpVersion(Command):
    """
    Increases the version number of a package, e.g. 1.0.0 > 1.0.1, assuming that semver is used

    bump
        {version? : The new version number}
        {--a|major : Bumps the major version e.g. 1.0.0 > 2.0.0}
        {--i|minor : Bumps the minor version e.g. 1.0.0 > 1.1.0}
    """

    def handle(self) -> None:
        config = self.get_package_config()

        if config:
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

        else:
            self.line('<error>No package found - Run `packagr init` first</error>')


class CreatePackage(Command):
    """
    Creates a new Packagr config file

    init
        {name? : The name of the package - default to the current folder name if not provided}
        {--o|overwrite : Overwrite existing without prompt}

    """

    def handle(self) -> None:
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
        if os.path.exists('packagr.toml'):
            if not overwrite:
                if not self.confirm('A package already exists at this location. Overwrite?', False, '(?i)^(y|j)'):
                    self.line('<error>Operation cancelled by user</error>')
                    return
        else:
            os.makedirs(name)

        self.write_package_content(template)
        response = 'Created config file `packagr.toml`'

        self.line(response)
