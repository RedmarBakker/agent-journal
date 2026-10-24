import time

from journal.repositories.outgoing_changes import OutgoingChanges
from journal.support.release import Release
from journal.sync.team_account import TeamAccount
from journal.version import VERSION

# how long the sync service's last word may be old before it counts as gone
STALE_SECONDS = 10


class SyncStatus:
    """How this journal's sync with its team server stands, in one line for the viewer's status bar: nothing in no team, the version to install when the team is pinned to a newer one, the fault while it cannot reach the server, that it is connecting before it first has, else how many changes wait to be sent; and which of those it is, for the Team page's dot and the top bar's Team button, nothing in no team."""

    def __init__(self, account: TeamAccount, outgoing: OutgoingChanges) -> None:
        self.account, self.outgoing = account, outgoing
        self.fault = ""
        self.reached = False
        self.reported_at: float | None = None

    def connected(self) -> None:
        self.fault = ""
        self.reached = True

    def failed(self, fault: str) -> None:
        self.fault = fault

    # the sync service's own word on how it stands: the fault it meets, and whether it has reached the team server
    def reported(self, fault: str, reached: bool) -> None:
        self.fault = fault
        self.reached = self.reached or reached
        self.reported_at = time.monotonic()

    # the fault the sync service last reported, or that it is gone when it has reported and then said nothing for a while; before
    # its first report the journal is still connecting
    def current_fault(self) -> str:
        if self.reported_at is not None and time.monotonic() - self.reported_at > STALE_SECONDS:
            return "the sync service is not running"
        return self.fault

    def upgrade_line(self) -> str:
        team_version = self.account.team_version()
        if not team_version or not Release(team_version).is_newer(Release(VERSION)):
            return ""
        return f"Not syncing: your team runs {team_version} and this journal {VERSION}; your changes wait here until you update it"

    def state(self) -> str:
        if not self.account.is_joined():
            return ""
        if self.upgrade_line():
            return "version"
        if self.current_fault():
            return "not_connected"
        if not self.reached:
            return "connecting"
        return "waiting" if self.waiting() else "in_step"

    def waiting(self) -> int:
        return len(self.outgoing.waiting())

    def line(self) -> str:
        if not self.account.is_joined():
            return ""
        if self.upgrade_line():
            return self.upgrade_line()
        if self.current_fault():
            return f"Not connected: {self.current_fault()}"
        if not self.reached:
            return "Connecting to the team server"
        waiting = self.waiting()
        if not waiting:
            return "In step with the team"
        return "1 change waiting" if waiting == 1 else f"{waiting} changes waiting"
