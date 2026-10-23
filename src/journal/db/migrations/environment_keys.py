from typing import ClassVar

from journal.db.migration import Migration


class EnvironmentKeys(Migration):
    """Every environment made before environments had keys is given its own random key, which never changes and is how this machine and a team server match it; the key is indexed, one environment to a key."""

    number: ClassVar[int] = 40
    statements: ClassVar[tuple[str, ...]] = (
        "UPDATE environments SET key = lower(hex(randomblob(16))) WHERE key IS NULL OR key = ''",
        "CREATE UNIQUE INDEX IF NOT EXISTS environments_key ON environments (key)",
    )
