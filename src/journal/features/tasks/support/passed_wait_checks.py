from collections.abc import Iterable

from journal.features.tasks.support.wait_checks import WaitChecks
from journal.repositories.checks import Checks
from journal.support.actor import Actor


class PassedWaitChecks:
    """The checks a wait made for itself that have passed or been removed, deleted once nothing waits on them; the ones still running stay."""

    def __init__(self, checks: Checks, wait_checks: WaitChecks) -> None:
        self.checks, self.wait_checks = checks, wait_checks

    def deleted(self, ids: Iterable[int], actor: Actor) -> None:
        for check in self.checks.resolved_waits_among(set(ids) - self.wait_checks.waited()):
            self.checks.delete(check, actor)
