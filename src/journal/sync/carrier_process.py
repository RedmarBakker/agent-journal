import os
import time

from journal.config import Config
from journal.sync.local_doors import LocalDoors
from journal.sync.sync_client import SyncClient
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink

# how often the carrier looks whether its journal and its team are still there
CHECK_SECONDS = 1.0


class CarrierProcess:
    """journal.py sync: the sync's carrier in a process of its own, the journal's child service where a supervisor hosts it, reaching the server's sync desk over its local doors; it ends when the journal server it lives for ends, or the journal leaves its team."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, config: Config, status: SyncStatus) -> None:
        self.account, self.link, self.config, self.status = account, link, config, status

    # parent is the process this one lives for, named before the journal was built, so a parent gone while it was built is noticed
    def run(self, parent: int) -> None:
        client = SyncClient(self.account, self.link, LocalDoors(self.config, os.environ.get("JOURNAL_ENV", "")), self.status)
        client.start()
        # the process ends at once, its loops with it: a batch it was sending stays outstanding at the desk and goes with the next carrier
        while self.is_alive(parent) and self.account.is_joined():
            time.sleep(CHECK_SECONDS)

    @staticmethod
    def is_alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        return True
