from dataclasses import dataclass


@dataclass(frozen=True)
class TeamEntry:
    """One connected team as the Team page lists it: its name here, its server's address, as whom and in which role, and how many people it has."""

    team: str
    address: str
    name: str
    role: str
    people: int
