import threading

from journal.app import App
from sync_service.carrier import Carrier
from sync_service.event_inbox import EventInbox
from sync_service.journal_doors import JournalDoors
from sync_service.team_link import TeamLink


class CarriedSync:
    """The sync service's carrier against an in-process journal's server: run in threads as the service's process runs it, or asked for one pull, one batch sent, a drain or an upgrade's finish at a time."""

    def __init__(self, app: App) -> None:
        app.server()
        self.carrier = Carrier(JournalDoors(app.config.root))
        self.inbox = EventInbox(self.carrier)

    def started(self) -> "CarriedSync":
        self.inbox.start()
        threading.Thread(target=self.carrier.run, args=(self.inbox.address,), name="carried sync", daemon=True).start()
        return self

    def stop(self) -> None:
        self.carrier.stop()
        self.inbox.stop()

    def team(self) -> TeamLink:
        return TeamLink(self.carrier.doors.team())

    def pulled(self) -> int:
        return self.carrier.pulled(self.team(), 0)

    def sent(self) -> bool:
        return self.carrier.carried(self.team(), self.carrier.doors.batch())

    def drained(self) -> dict:
        return self.carrier.drained()

    def upgrade_finished(self) -> None:
        self.carrier.upgrade_finished(self.team())
        self.carrier.heard({"event": "upgrade_abandoned"})
