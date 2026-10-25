from journal.features.seed import Seed
from journal.features.tasks.support.wait_checks import WaitChecks
from journal.repositories.checks import Checks
from journal.support.actor import Actor


class LeftWaitChecks(Seed):
    """At boot, the checks earlier waits made for themselves that nothing waits on any more are deleted."""

    def __init__(self, checks: Checks, wait_checks: WaitChecks) -> None:
        self.checks, self.wait_checks = checks, wait_checks

    def run(self) -> None:
        self.wait_checks.deleted([check.id for check in self.checks.wait_rows()], Actor.system())
