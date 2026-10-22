from enum import StrEnum


class MigrationState(StrEnum):
    """The state of migrating a version 3 journal: offered at first, postponed by the user, in progress, or done."""

    OFFERED = "offered"
    LATER = "later"
    BUSY = "running"
    FINISHED = "done"

    def is_open(self) -> bool:
        return self in (MigrationState.OFFERED, MigrationState.LATER)
