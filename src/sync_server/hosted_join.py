from dataclasses import dataclass


@dataclass(frozen=True)
class HostedJoin:
    """What the team server's own hosted journal joins with: the invitation code, the service account's email, name and password, and the version the team is pinned to."""

    code: str
    email: str
    name: str
    password: str
    version: str
