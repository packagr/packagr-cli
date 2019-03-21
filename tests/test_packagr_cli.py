import unittest
import mock
from cleo import CommandTester
from packagr.packagr import application
from packagr.commands.base import Command
from packagr import utilities
from packagr.objects import Package, Token, User


class MockIO(object):
    _out = []

    def __init__(self, *args, **kwargs):
        pass

    def write_line(self, styled, verbosity):
        self._out.append(styled)


class MockRequest:
    def __init__(self, *args, **kwargs):
        pass

    status_code = 200

    def json(self):
        return {
            'profile': {
                'hash_id': '1234'
            }
        }


def gen_response(code, resp):
    class Response:
        status_code = code

        def __init__(self, *args, **kwargs):
            pass

        def json(self):
            return resp

    return Response


class MockTokenRequest:
    def __init__(self, *args, **kwargs):
        pass

    status_code = 200

    def json(self):
        return [{'name': 'test'}]


mock_package_config = {
    'name': 'test',
    'version': '0.1.0',
    'array': ['grr'],
    'grr': 'arg',
    'hash-id': '1234'
}

mock_global_config = {
    'hash-id': '1234',
    'email': 'me@test.com',
    'password': 'password',
    'url': 'www.example.com'
}


def mock_os_walk(dir):
    yield dir, 'dirs', ['file1']


def mock_os_walk_alt(dir):
    yield dir, 'dirs', []


@mock.patch('requests.post', MockRequest)
@mock.patch.object(Command, 'get_package_config', mock.MagicMock(return_value=mock_package_config))
@mock.patch.object(Command, 'get_global_config', mock.MagicMock(return_value=mock_global_config))
class CliTests(unittest.TestCase):
    def test_configure(self, *args):
        command = application.find('configure')
        tester = CommandTester(command)
        tester.execute("1234 test@test.com password")

        self.assertIn('Successfully updated config file', tester.io.fetch_output())

    def test_set(self):
        command = application.find('set')
        tester = CommandTester(command)
        tester.execute('foo bar')
        self.assertIn('Successfully added key "foo" with value "bar"', tester.io.fetch_output())

        add_command = application.find('add')
        add_tester = CommandTester(add_command)
        add_tester.execute('foo2 bar')

        tester.execute('foo2 bar2', inputs='no')
        self.assertIn('Operation cancelled by user', tester.io.fetch_output())

    def test_add(self):
        command = application.find('add')
        tester = CommandTester(command)

        tester.execute('array bar')
        self.assertIn('Successfully added key "array" with value "bar"', tester.io.fetch_output())

        tester.execute('grr bar2')
        self.assertIn('Cannot add to value grr because it is not an array', tester.io.fetch_output())

    def test_remove(self):
        command = application.find('remove')
        tester = CommandTester(command)

        tester.execute('array grr')
        self.assertIn('Successfully removed value grr from array "array"', tester.io.fetch_output())

        tester.execute('grr bar2')
        self.assertIn('Cannot remove item because the property is not an array', tester.io.fetch_output())

        tester.execute('grrrrr bar2')
        self.assertIn('Cannot remove item because the property grrrrr does not exist', tester.io.fetch_output())

    @mock.patch('packagr.utilities.check_configuration', mock.MagicMock(return_value=True))
    def test_install_uninstall(self):
        command = application.find('install')
        tester = CommandTester(command)

        with mock.patch('subprocess.call', mock.MagicMock(return_value=0)):
            tester.execute('foo')
            self.assertIn('Installed package foo and added it to the config', tester.io.fetch_output())

            with mock.patch.object(Command, 'append', mock.MagicMock(return_value=None)):
                tester.execute('foo')
                self.assertIn('Package foo was installed', tester.io.fetch_output())

        with mock.patch('subprocess.call', mock.MagicMock(return_value=1)):
            tester.execute('foo2')
            self.assertIn('Error installing package foo2', tester.io.fetch_output())

        command = application.find('uninstall')
        tester = CommandTester(command)

        with mock.patch('subprocess.call', mock.MagicMock(return_value=0)):
            tester.execute('foo --skip-prompts')
            self.assertIn('Successfully uninstalled foo', tester.io.fetch_output())

        with mock.patch('subprocess.call', mock.MagicMock(return_value=1)):
            tester.execute('foo3')
            self.assertIn('Error uninstalling package foo3.', tester.io.fetch_output())

    def test_bump(self):
        command = application.find('bump')
        tester = CommandTester(command)

        tester.execute()
        self.assertIn('Updated version to 0.1.1', tester.io.fetch_output())

        tester.execute('--minor')
        self.assertIn('Updated version to 0.2.1', tester.io.fetch_output())

        tester.execute('--major')
        self.assertIn('Updated version to 1.2.1', tester.io.fetch_output())

        tester.execute('some_version')
        self.assertIn('Updated version to some_version', tester.io.fetch_output())

        tester.execute('some_version --major')
        self.assertIn('Cannot use the version argument with either the --minor or --major arguments',
                      tester.io.fetch_output())

        tester.execute()
        self.assertIn('Cannot automatically bump version because this package does not appear to use Semver',
                      tester.io.fetch_output())

    @mock.patch('distutils.core.setup')
    def test_package(self, *args):
        command = application.find('package')
        tester = CommandTester(command)
        tester.execute()
        self.assertIn('Package built', tester.io.fetch_output())

        tester.execute('--no-wheel --no-sdist')
        self.assertIn('No formats to build!', tester.io.fetch_output())

    @mock.patch('builtins.open')
    @mock.patch.object(Command, 'check_configuration', mock.MagicMock(return_value=mock_global_config))
    def test_upload(self, *args):
        command = application.find('upload')
        tester = CommandTester(command)

        with mock.patch('os.walk', mock_os_walk):
            with mock.patch('requests.post', MockRequest) as mock_request:
                mock_request.status_code = 201
                tester.execute()
                self.assertIn('Uploaded 1 files successfully', tester.io.fetch_output())

                mock_request.status_code = 409
                tester.execute()
                self.assertIn('Package failed to upload. Status code: 409', tester.io.fetch_output())

                tester.execute('--ignore-errors')
                self.assertIn('Skipping to the next file...', tester.io.fetch_output())

        with mock.patch('os.walk', mock_os_walk_alt):
            with mock.patch('requests.post', MockRequest) as mock_request:
                mock_request.status_code = 201
                tester.execute()
                self.assertIn('Nothing to upload. Run `packagr build` first to build a package', tester.io.fetch_output())


class InitTestCase(unittest.TestCase):
    @mock.patch('os.makedirs')
    def test_init(self, *args):
        command = application.find('init')
        tester = CommandTester(command)

        with mock.patch('os.path.exists', mock.MagicMock(return_value=False)):
            tester.execute(inputs='yes')
            self.assertIn('Created config file `packagr.toml`', tester.io.fetch_output())

        with mock.patch('os.path.exists', mock.MagicMock(return_value=True)):
            tester.execute(inputs='no')
            self.assertIn('Operation cancelled by user', tester.io.fetch_output())


@mock.patch.object(Command, 'get_package_config', mock.MagicMock(return_value=None))
class NoPackageTestCase(unittest.TestCase):
    def helper(self, cmd: str, args: str = 'foo bar') -> None:
        command = application.find(cmd)
        tester = CommandTester(command)
        tester.execute(args)
        self.assertIn('No package found - Run `packagr init` first\n', tester.io.fetch_output())

    def test_set(self):
        self.helper('set')

    def test_add(self):
        self.helper('add')

    def test_uninstall(self):
        self.helper('uninstall', 'foo')

    def test_bump(self):
        self.helper('bump', '')

    def test_remove(self):
        self.helper('remove')


class InvalidGlobalConfigTestCase(unittest.TestCase):
    def helper(self, cmd: str, args: str = 'foo') -> None:
        command = application.find(cmd)
        tester = CommandTester(command)

        with mock.patch.object(Command, 'get_global_config', mock.MagicMock(return_value=None)):
            tester.execute(args)
            self.assertIn('Global config not found', tester.io.fetch_output())

        with mock.patch.object(Command, 'get_global_config', mock.MagicMock(return_value=mock_global_config)):
            with mock.patch.object(Command, 'check_configuration', mock.MagicMock(return_value=False)):
                tester.execute(args)
                self.assertIn('Packagr credentials are invalid', tester.io.fetch_output())

    def test_install(self):
        self.helper('install')

    def test_upload(self):
        self.helper('upload', '')


@mock.patch('requests.post', MockRequest)
@mock.patch('subprocess.call', mock.MagicMock(return_value=0))
class BaseCommandTestCase(unittest.TestCase):

    def test_check_configuration(self):
        command = application.find('configure')
        tester = CommandTester(command)
        with mock.patch('packagr.utilities.check_configuration', mock.MagicMock()) as mock_global_config:
            mock_global_config.side_effect = AssertionError('test')
            tester.execute('1234 test password')

        self.assertIn('Invalid credentials', tester.io.fetch_output())

    def test_get_global_config(self):
        with mock.patch.object(Command, 'get_package_config', mock.MagicMock()):
            command = application.find('install')
            tester = CommandTester(command)
            tester.execute('foo')
            self.assertIn('Packagr credentials are invalid', tester.io.fetch_output())

    def test_get_package_config(self):
        with mock.patch('packagr.utilities.get_package_config', mock.MagicMock(return_value=None)):
            command = application.find('add')
            tester = CommandTester(command)
            tester.execute('foor bar')
            self.assertIn('Unable to perform this action because no package exists at the current location',
                          tester.io.fetch_output())


@mock.patch('packagr.utilities.check_configuration', mock.MagicMock(return_value=True))
@mock.patch('packagr.utilities.get_access_token', mock.MagicMock(return_value='1234'))
@mock.patch.object(Command, 'get_global_config', mock.MagicMock(return_value=mock_global_config))
class TokenTestCase(unittest.TestCase):
    def test_create(self):
        command = application.find('create-token')
        tester = CommandTester(command)
        with mock.patch('packagr.utilities.get_packages',
                        mock.MagicMock(return_value=[Package('test', '1234')])) as mock_packages:
            with mock.patch('packagr.utilities.get_users', mock.MagicMock(return_value=[User('test', '1234')])):
                with mock.patch('packagr.utilities.get_users',
                                mock.MagicMock(return_value=[User('test', '1234')])) as mock_users:
                    with mock.patch('packagr.utilities.create_access_token',
                                    mock.MagicMock(return_value=(True, None))) as mock_create_access_token:
                        tester.execute('test test')
                        self.assertIn('Access token created', tester.io.fetch_output())

                        mock_create_access_token.return_value = False, 'error'
                        tester.execute('test test')
                        self.assertIn('Could not create access token due to error error', tester.io.fetch_output())

                    mock_users.return_value = []
                    tester.execute('test test')
                    self.assertIn('Cannot find a user with that email', tester.io.fetch_output())

                    mock_packages.return_value = []
                    tester.execute('test test')
                    self.assertIn('Cannot find a package with that name', tester.io.fetch_output())

    def test_delete(self):
        command = application.find('delete-token')
        tester = CommandTester(command)

        with mock.patch('packagr.utilities.get_packages',
                        mock.MagicMock(return_value=[Package('package', '1234')])) as mock_packages:
            with mock.patch('packagr.utilities.get_users', mock.MagicMock(return_value=[User('test', '1234')])):
                with mock.patch('packagr.utilities.get_users',
                                mock.MagicMock(
                                    return_value=[User(email='me@email.com', hash_id='hash')])
                                ) as mock_users:
                    with mock.patch('packagr.utilities.get_tokens',
                                    mock.MagicMock(return_value=
                                                   [Token(uuid='1234', user='hash', package='1234')])
                                    ) as mock_get_tokens:
                        with mock.patch('packagr.utilities.delete_access_token',
                                        mock.MagicMock(return_value=(True, None))) as mock_delete:
                            tester.execute('package me@email.com')
                            self.assertIn('Access token deleted', tester.io.fetch_output())

                            mock_delete.return_value = False, 'a test error'
                            tester.execute('package me@email.com')
                            self.assertIn('a test error', tester.io.fetch_output())

                            mock_get_tokens.return_value = []
                            tester.execute('package me@email.com')
                            self.assertIn('Cannot delete access token for this package/user combination',
                                          tester.io.fetch_output())

                            mock_users.return_value = []
                            tester.execute('package me@email.com')
                            self.assertIn('Cannot find a user with that email',
                                          tester.io.fetch_output())

                            mock_packages.return_value = []
                            tester.execute('package me@email.com')
                            self.assertIn('Cannot find a package with that name',
                                          tester.io.fetch_output())


class UtilitiesTestCase(unittest.TestCase):
    @mock.patch('packagr.utilities.check_configuration', mock.MagicMock(return_value=True))
    @mock.patch('packagr.utilities.get_package_config', mock.MagicMock(return_value=mock_global_config))
    def test_get_access_token(self):
        with mock.patch('requests.post', gen_response(200, {'token': '1234'})):
            token = utilities.get_access_token()
            self.assertEqual(token, '1234')

        with mock.patch('requests.post', gen_response(400, {})):
            token = utilities.get_access_token()
            self.assertIsNone((token))

    def test_get_packages(self):
        with mock.patch('requests.get', gen_response(200, [{'name': 'test', 'uuid': '1234'}])):
            packages = utilities.get_packages({})
            self.assertEqual(len(packages), 1)

    def test_get_tokens(self):
        with mock.patch('requests.get', gen_response(200, [{'package': 'test', 'user': 'test', 'uuid': '1234'}])):
            tokens = utilities.get_tokens({})
            self.assertEqual(len(tokens), 1)

        with mock.patch('requests.get', gen_response(400, [{'package': 'test', 'user': 'test', 'uuid': '1234'}])):
            tokens = utilities.get_tokens({})
            self.assertIsNone(tokens)

    def test_get_users(self):
        with mock.patch('requests.get', gen_response(200, [{'email': 'test', 'hash_id': 'test'}])):
            users = utilities.get_users({})
            self.assertEqual(len(users), 1)

    def test_create_access_token(self):
        with mock.patch('requests.post', gen_response(201, None)):
            status, response = utilities.create_access_token({}, Package('test', '1234'), User('test', '1234'))
            self.assertTrue(status)
            self.assertIsNone(response)

        with mock.patch('requests.post', gen_response(400, None)):
            status, response = utilities.create_access_token({}, Package('test', '1234'), User('test', '1234'))
            self.assertFalse(status)
            self.assertEqual(response, 400)

    @mock.patch('packagr.utilities.check_configuration', mock.MagicMock(return_value=True))
    def test_delete_access_token(self):
        with mock.patch('packagr.utilities.get_package_config',
                        mock.MagicMock(return_value=mock_package_config)) as mock_config:
            with mock.patch('requests.delete', gen_response(204, {})):
                deleted, error = utilities.delete_access_token(Token('1234', 'test', 'test'), {})
                self.assertTrue(deleted)
                self.assertIsNone(error)

                deleted, error = utilities.delete_access_token(Token('1234', 'test', '1234'), {})
                self.assertFalse(deleted)
                self.assertEqual(error, 'Cannot delete access tokens belonging to the account owner')

            with mock.patch('requests.delete', gen_response(400, {})):
                deleted, error = utilities.delete_access_token(Token('1234', 'test', 'test'), {})
                self.assertFalse(deleted)
                self.assertEqual(error, 'Could not delete access token due to 400 error')

            mock_config.return_value = None
            deleted, error = utilities.delete_access_token(Token('1234', 'test', 'test'), {})
            self.assertFalse(deleted)
            self.assertEqual(error, 'Package config not found')


class ObjectTestCase(unittest.TestCase):
    def test_object_strings(self):
        pkg = Package('test', '1234')
        self.assertEqual('test', str(pkg))

        user = User('test', '1234')
        self.assertEqual('test', str(user))


class AuthTokenTestCase(unittest.TestCase):
    @mock.patch('packagr.utilities.get_access_token', mock.MagicMock(return_value=None))
    def test_create(self):
        command = application.find('create-token')
        tester = CommandTester(command)
        tester.execute('test test')
        self.assertIn('Unable to get login token from Packagr', tester.io.fetch_output())


if __name__ == '__main__':
    unittest.main()
