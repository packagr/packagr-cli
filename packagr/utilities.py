import toml
from typing import Any, MutableMapping


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
