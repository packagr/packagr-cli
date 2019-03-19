import toml
from typing import Any, MutableMapping
import requests


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
