from typing import ClassVar

from journal.db.migration import Migration


class PluginsOffOnPurpose(Migration):
    """A plugin already off when the journal learned to tell a switch-off on purpose from a plugin it stopped is taken as switched off on purpose."""

    number: ClassVar[int] = 44
    statements: ClassVar[tuple[str, ...]] = ("UPDATE plugins SET off_on_purpose = 1 WHERE enabled = 0",)
