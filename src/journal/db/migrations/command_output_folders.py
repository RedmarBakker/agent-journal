from typing import ClassVar

from journal.db.migration import Migration


class CommandOutputFolders(Migration):
    """Every output stored before an output recorded the folder it ran in ran in none that is known."""

    number: ClassVar[int] = 53
    statements: ClassVar[tuple[str, ...]] = ("UPDATE command_outputs SET ran_in = '' WHERE ran_in IS NULL",)
