import toml
from typing import Any, MutableMapping, Optional, List, Tuple
from packagr.objects import Package, Token, User
import requests
import os


def get_package_config(path: str = 'packagr.toml') -> MutableMapping:
    """
    Returns the content of the package config file as a dict
    """
    with open(path, 'r') as f:
        config: MutableMapping[str, Any] = toml.loads(f.read())
        return config


def write_package_content(config: dict, path: str = 'packagr.toml') -> None:
    """
    Writes a given dict to the package config file
    """
    with open(path, 'w') as f:
        f.write(toml.dumps(config))


def check_configuration(hash_id: str, email: str, password: str) -> bool:
    post = {
        'email'   : email,
        'password': password
    }
    response = requests.post('https://api.packagr.app/api/auth/login/', post)
    assert response.status_code == 200
    assert response.json().get('profile', {}).get('hash_id') == hash_id
    return True


def get_access_token(path: str = None):
    if not path:
        path = os.path.expanduser('~/packagr_conf.toml')
    config = get_package_config(path=path)

    if check_configuration(config['hash-id'], config['email'], config['password']):
        post = {
            'email': config['email'],
            'password': config['password']
        }
        response = requests.post('https://api.packagr.app/api/auth/login/', post)

        try:
            assert response.status_code == 200
            token = response.json()['token']
            return token

        except AssertionError:
            return None


def get_packages(headers: dict) -> Optional[List[Package]]:
    response = requests.get('https://api.packagr.app/api/v1/packages/', headers=headers)

    try:
        assert response.status_code == 200
    except AssertionError:
        return None

    packages = []
    for pkg in response.json():
        packages.append(Package(**pkg))

    return packages


def get_tokens(headers: dict) -> Optional[List[Token]]:
    response = requests.get('https://api.packagr.app/api/v1/tokens/', headers=headers)

    try:
        assert response.status_code == 200
    except AssertionError:
        return None

    tokens = []
    for token in response.json():
        tokens.append(Token(**token))

    return tokens


def get_users(headers: dict) -> Optional[List[User]]:
    response = requests.get('https://api.packagr.app/api/v1/subusers/', headers=headers)

    try:
        assert response.status_code == 200
    except AssertionError:
        return None

    users = []
    for usr in response.json():
        users.append(User(**usr))

    return users


def create_access_token(
        headers: dict,
        package: Package,
        user: User,
        write_access: bool = False) -> Tuple[bool, Optional[int]]:
    """
    Create an access token for a specific package/user combination
    """
    post = {
        'user': user.hash_id,
        'package': package.uuid,
        'write_access': write_access
    }
    response = requests.post('https://api.packagr.app/api/v1/tokens/',  post, headers=headers)

    try:
        assert response.status_code == 201
        return True, None
    except AssertionError:
        return False, response.status_code


def delete_access_token(token: Token, headers: dict, path: str = None) -> Tuple[bool, Optional[str]]:
    if not path:
        path = os.path.expanduser('~/packagr_conf.toml')

    config = get_package_config(path=path)

    if config:
        try:
            assert token.user is not config['hash-id']
        except AssertionError:
            return False, 'Cannot delete access tokens belonging to the account owner'

        response = requests.delete(f'https://api.packagr.app/api/v1/tokens/{token.uuid}/', headers=headers)

        try:
            assert response.status_code == 204
            return True, None
        except AssertionError:
            return False, f'Could not delete access token due to {response.status_code} error'

    return False, 'Package config not found'
