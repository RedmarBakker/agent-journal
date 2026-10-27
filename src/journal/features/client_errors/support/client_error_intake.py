from journal.events.announcer import Announcer
from journal.events.rows.client_error_logged import ClientErrorLogged
from journal.features.client_errors.support.client_error_store import ClientErrorStore


class ClientErrorIntake:
    """Keeps an error the viewer posted, and announces one the store did not hold, so the conduct tells the agent of it once."""

    def __init__(self, store: ClientErrorStore, announcer: Announcer) -> None:
        self.store, self.announcer = store, announcer

    def record(self, message: str, stack: str) -> None:
        if self.store.add(message, stack):
            self.announcer.announce(ClientErrorLogged(count=self.store.count()))
