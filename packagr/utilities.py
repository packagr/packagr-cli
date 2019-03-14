import toml


def get_package_config() -> dict:
    """
    Returns the content of the package config file as a dict
    """
    with open('packagr.toml', 'r') as f:
        return toml.loads(f.read())


def write_package_content(config: dict) -> None:
    """
    Writes a given dict to the package config file
    """
    with open('packagr.toml', 'w') as f:
        f.write(toml.dumps(config))
