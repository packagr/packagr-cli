from packagr.commands.base import Command
from distutils import core as dist_core
from packagr.utilities import get_package_config
import os
import requests
from typing import List, Dict
import setuptools #  DO NOT REMOVE THIS - IT IS IMPORTANT, EVEN THOUGH IT APPEARS TO NOT BE USED


class CreatePackage(Command):
    """
    Creates sdist wheel packages

    package
        {--w|no-wheel : Don't create a wheel package}
        {--s|no-sdist : Don't create an sdist package}
    """
    def create_config(self, formats: List[str]) -> dict:
        config = get_package_config()

        output = {
            'script_name': 'setup.py',
            'script_args': formats + ['clean', '--all',]
        }

        for key, value in config.items():
            output[key] = value

        return output

    def handle(self) -> None:
        formats: list = ['bdist_wheel', 'sdist']

        if self.option('no-wheel'):
            formats.remove('bdist_wheel')
        if self.option('no-sdist'):
            formats.remove('sdist')

        if not formats:
            self.line('<error>No formats to build!</error>')
            return

        config = self.create_config(formats)
        dist_core.setup(**config)
        self.line('<info>Package built</info>')


class UploadPackage(Command):
    """
    Uploads built packages to Packagr

    upload
        {--i|ignore-errors : Continue to the next file even if errors are encountered}
    """

    def handle(self) -> None:
        config = self.get_global_config()

        if config:
            if self.check_configuration(config['hash-id'], config['email'], config['password']):

                package_config = self.get_package_config()

                if package_config:
                    ignore_errors = self.option('ignore-errors')

                    upload_count = 0

                    for root, dirs, files in os.walk('dist'):
                        if len(files) == 0:
                            self.line('<error>Nothing to upload. Run `packagr build` first to build a package</error>')
                            return

                        for file in files:
                            self.line(f'<comment>Attempting to upload file {file} to Packagr</comment>')

                            _files = {'content': (file, open(os.path.join(root, file), 'rb'))}

                            headers: Dict[str, str] = {}
                            response = requests.post(
                                config['url'],
                                auth=(config['email'], config['password']),
                                data={'name': package_config['name'], 'version': package_config['version']},
                                files=_files,
                                headers=headers
                            )

                            try:
                                assert response.status_code == 201
                                self.line(f'<info>File {file} uploaded successfully')
                                upload_count += 1
                            except AssertionError:

                                if ignore_errors:
                                    self.line(f'<error>Package failed to upload. Status code: {response.status_code}'
                                              f'\nSkipping to the next file...</error>')
                                else:
                                    self.line(f'<error>Package failed to upload. Status code: {response.status_code}</error>')
                                    return

                    if upload_count == 0:
                        self.line('<error>No files uploaded</error>')
                    else:
                        self.line(f'<info>Uploaded {upload_count} files successfully</info>')

            else:
                self.line('<error>Packagr credentials are invalid</error>')

        else:
            self.line('<error>Global config not found</error>')
