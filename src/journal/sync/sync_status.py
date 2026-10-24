from journal.repositories.outgoing_changes import OutgoingChanges
from journal.support.release import Release
from journal.sync.carrier_beat import CarrierBeat
from journal.sync.team_account import TeamAccount
from journal.version import VERSION


class SyncStatus:
    """How this journal's sync with its team server stands, in one line for the viewer's status bar: nothing in no team, the version to install when the team is pinned to a newer one, the fault while it cannot reach the server, that it is connecting before it first has, else how many changes wait to be sent; and which of those it is, for the Team page's dot and the top bar's Team button, nothing in no team."""

    def __init__(self, account: TeamAccount, outgoing: OutgoingChanges, beat: CarrierBeat) -> None:
        self.account, self.outgoing, self.beat = account, outgoing, beat
        self.fault = ""
        self.reached = False

    def connected(self) -> None:
        self.fault = ""
        self.reached = True

    def failed(self, fault: str) -> None:
        self.fault = fault

    # the fault met here, or by the carrier in its own process, as its beat file says
    def current_fault(self) -> str:
        return self.fault or self.beat.fault()

    # where the carrier runs: in a process of its own, which beats into its file, or in the server's own threads
    def runs(self) -> str:
        return "process" if self.beat.path.is_file() else "server"

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
