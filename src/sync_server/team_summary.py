from dataclasses import dataclass


@dataclass(frozen=True)
class TeamSummary:
    """What anyone may ask a team server before joining it: the first commit of the repository its journal belongs to, whether it holds a journal yet, the journal version the team is pinned to, the migration its rows are at, whether a journal must run exactly that version to sync, whether it has an admin, without whom its first connection makes one, and the team's key, name and number T."""

    repository: str
    has_rows: bool
    version: str = ""
    migration: int = 0
    versions: str = "exact"
    has_admin: bool = True
    key: str = ""
    name: str = ""
    number: int = 0
