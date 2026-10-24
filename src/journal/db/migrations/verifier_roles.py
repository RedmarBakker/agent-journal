from typing import ClassVar

from journal.db.migration import Migration


class VerifierRoles(Migration):
    """A verifier sent before a worker's row named its role takes the verifier's role, found by its link to the row it judged."""

    number: ClassVar[int] = 45
    statements: ClassVar[tuple[str, ...]] = ("UPDATE workers SET role = 'verifier' WHERE 'workers:' || id IN (SELECT source FROM links WHERE kind = 'verifies')",)
