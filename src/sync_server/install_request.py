from dataclasses import dataclass


@dataclass(frozen=True)
class InstallRequest:
    """The first connection to a team server with no account yet: the email, name and password of the person who becomes its admin, and a name for this machine."""

    email: str
    name: str
    password: str
    device_name: str
