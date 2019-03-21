class Package(object):
    def __init__(self, name: str, uuid: str, *args, **kwargs) -> None:
        self.name: str = name
        self.uuid: str = uuid

    def __str__(self) -> str:
        return self.name


class User(object):
    def __init__(self, email: str, hash_id: str, *args, **kwargs) -> None:
        self.email = email
        self.hash_id = hash_id

    def __str__(self) -> str:
        return self.email


class Token(object):
    def __init__(self, uuid: str, package: str, user: str, *args, **kwargs) -> None:
        self.uuid = uuid
        self.package = package
        self.user = user
