from cleo import Command
import os
import toml


class ConfigureClient(Command):
    """
    Configure the CLI for your Packagr account

    configure
        {hash-id? : TYour Packagr account hash ID}
        {api-access-key? : Your API access key}

    """

    def handle(self):
        """
        Creates a packagr config file at the root directory

        TODO: Need to update this to actually validate the hash_id and api_access_key before setting these values
        """

        hash_id: str = self.argument('hash-id')
        api_access_key: str = self.argument('api-access-key')

        config_path = os.path.expanduser('~')

        content = {
            'url': 'https://api.packagr.app/%s/' % hash_id,
            'api_access_key': api_access_key
        }

        with open(os.path.join(config_path, 'packagr_conf.toml'), 'w') as f:
            f.write(toml.dumps(content))

        self.line('Successfully updated config file')


class CreatePackage(Command):
    """
    Creates a new Packagr config file

    create
        {name? : The name of the package}
        {--o|overwrite : Overwrite existing without prompt}

    """

    def handle(self):
        """
        Creates a file called `packagr.toml` in the current directory

        Checks if file exists first, prompts to replace

        """
        name = self.argument('name')
        overwrite = self.option('overwrite')

        template = {
            'name': name,
            'version': '0.1.0',
        }

        if os.path.exists('packagr.toml') and not overwrite:
            if not self.confirm('A package already exists at this location. Overwrite?', False, '(?i)^(y|j)'):
                return

        with open('packagr.toml', 'w') as f:
            f.write(toml.dumps(template))

        response = 'Created config file `packagr.toml`'

        self.line(response)
