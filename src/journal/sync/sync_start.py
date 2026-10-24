import os
import sys
from pathlib import Path

from journal.config import Config
from journal.supervisor_link import JOURNAL, SupervisorLink
from journal.sync.sync_client import SyncClient
from journal.sync.team_account import TeamAccount

CARRIER = "sync"


class SyncStart:
    """Where a joined journal's sync runs: as the journal's child service in a process of its own (journal.py sync) where a supervisor hosts the journal, so it is kept alive and stopped with the journal, else in the server's own threads; stopped the same way it was started."""

    def __init__(self, link: SupervisorLink, account: TeamAccount, client: SyncClient, config: Config) -> None:
        self.link, self.account, self.client, self.config = link, account, client, config

    def run(self) -> None:
        if not self.account.is_joined():
            return
        host = self.link.hosting()
        if host is None:
            self.client.start()
            return
        package = Path(__file__).resolve().parents[2]
        environ = {**os.environ, "JOURNAL_ROOT": str(self.config.root)}
        self.link.start_child(host, CARRIER, JOURNAL, [sys.executable, str(package / "journal.py"), "sync"], self.config.root, environ, self.config.home / "runtime" / f"{CARRIER}.log")

    def stopped(self) -> None:
        host = self.link.hosting()
        if host is None:
            self.client.stop()
            return
        self.link.stop_service(host, CARRIER)
