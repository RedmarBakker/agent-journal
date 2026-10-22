from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneData:
    """What the phone app is given about itself: its name and number, when its pairing ends, the environment it shows, and the project, with its colour."""

    phone: str
    id: int
    expires: str
    environment: str
    project: str
    color: str
