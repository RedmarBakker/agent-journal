from typing import ClassVar

from journal.db.migration import Migration


class PlanModeChoice(Migration):
    """Existing plans have not explicitly chosen a mode."""

    number: ClassVar[int] = 88
    statements: ClassVar[tuple[str, ...]] = ("UPDATE plans SET mode_chosen = 0 WHERE mode_chosen IS NULL",)
