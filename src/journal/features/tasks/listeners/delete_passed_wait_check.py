from journal.events.listener import Listener
from journal.events.rows.row_resolved import RowResolved
from journal.features.tasks.support.wait_checks import WaitChecks
from journal.models.check import Check
from journal.support.actor import Actor


class DeletePassedWaitCheck(Listener[RowResolved]):
    """A check a wait made for itself that passed is deleted once nothing waits on it, so the agent is informed of it once."""

    def __init__(self, wait_checks: WaitChecks) -> None:
        self.wait_checks = wait_checks

    def handle(self, event: RowResolved) -> None:
        table, _, number = event.ref.partition(":")
        if table == Check.table() and number.isdigit():
            self.wait_checks.deleted([int(number)], Actor.system())
