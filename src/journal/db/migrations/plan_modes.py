from typing import ClassVar

from journal.db.migration import Migration


class PlanModes(Migration):
    """Every plan made before plans had a mode is a solo one, since it has no rig."""

    number: ClassVar[int] = 76
    statements: ClassVar[tuple[str, ...]] = ("UPDATE plans SET mode = 'solo' WHERE mode IS NULL",)
