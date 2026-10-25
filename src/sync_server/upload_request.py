from dataclasses import dataclass

from sync_server.copied_row import CopiedRow


@dataclass(frozen=True)
class UploadRequest:
    """A journal's first full copy: every row, the highest number each table had, the first commit of the repository it belongs to, the version of the journal that made it, which the team is then pinned to, the migration its rows are at, and the name it gives the team."""

    rows: tuple[CopiedRow, ...]
    highest: dict
    repository: str
    version: str
    migration: int
    team_name: str = ""

    @classmethod
    def parsed(cls, rows: list, highest: dict, repository: str, version: str, migration: int, team_name: str = "") -> "UploadRequest":
        return cls(tuple(CopiedRow(**row) for row in rows), dict(highest), repository, version, int(migration), team_name)
