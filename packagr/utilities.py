import toml


def get_package_config(path: str = 'packagr.toml') -> dict:
    """
    Returns the content of the package config file as a dict
    """
    with open(path, 'r') as f:
        return toml.loads(f.read())


def write_package_content(config: dict, path: str = 'packagr.toml') -> None:
    """
    Writes a given dict to the package config file
    """
    with open(path, 'w') as f:
        f.write(toml.dumps(config))
