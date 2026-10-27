from dataclasses import dataclass


@dataclass(frozen=True)
class LibraryAnswer:
    """What GET /library tells any caller, a token or none: the team's name and key, the server's protocol, whether it has an admin yet, and the caller's role, empty without a token."""

    name: str
    key: str
    protocol: int
    has_admin: bool
    role: str
