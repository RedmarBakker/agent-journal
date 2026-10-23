from dataclasses import dataclass


@dataclass(frozen=True)
class AcceptRequest:
    """A person taking up an invitation: the code, the email it was made for, their name, the password typed twice, and a name for this machine."""

    code: str
    email: str
    name: str
    password: str
    password_repeat: str
    device_name: str
