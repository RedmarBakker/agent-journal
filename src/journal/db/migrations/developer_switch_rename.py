from typing import ClassVar

from journal.db.migration import Migration


class DeveloperSwitchRename(Migration):
    """The Developer features switch is now the switch of the Slow requests feature, so each stored value of the old option moves to the feature's key and keeps its row."""

    number: ClassVar[int] = 82
    statements: ClassVar[tuple[str, ...]] = ("UPDATE settings SET key = 'features.faults' WHERE key = 'faults.developer'",)
