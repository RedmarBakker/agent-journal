from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordRequest:
    """A person changing their own password: the one they have and the one they choose."""

    old: str
    new: str
