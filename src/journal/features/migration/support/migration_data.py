from dataclasses import dataclass


@dataclass(frozen=True)
class MigrationData:
    """The migration feature's reading: whether a version 3 journal is waiting to be migrated."""

    version_3_waiting: bool
