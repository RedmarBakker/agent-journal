from typing import ClassVar

from journal.db.migration import Migration


class EnvironmentKinds(Migration):
    """Every environment made before environments had a kind is a local one, of no team."""

    number: ClassVar[int] = 51
    statements: ClassVar[tuple[str, ...]] = (
        "UPDATE environments SET kind = 'local' WHERE kind IS NULL",
        "UPDATE environments SET team_key = '' WHERE team_key IS NULL",
    )
