from dataclasses import dataclass


@dataclass(frozen=True)
class InstallRequest:
    """The first connection to a team server with no account yet: the email, name and password of the person who becomes its admin, a name for this machine, and the setup code the server's installer printed."""

    email: str
    name: str
    password: str
    device_name: str
    setup_code: str = ""
