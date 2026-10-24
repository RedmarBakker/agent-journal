from journal.features.client_errors.client_errors_nudges import ClientErrorsNudges
from journal.features.client_errors.support.client_error_store import ClientErrorStore
from journal.features.client_errors.support.client_errors_data import ClientErrorsData
from journal.models.agent import Agent
from journal.repositories.entries import Entries

REMINDER_TOOL_USES = 50


class ClientErrorsDataReader:
    """The viewer errors still in the store, and whether this session was told of them within the last fifty of its tool uses."""

    def __init__(self, store: ClientErrorStore, entries: Entries) -> None:
        self.store, self.entries = store, entries

    def read(self, agent: Agent) -> ClientErrorsData:
        count = self.store.count()
        if not count:
            return ClientErrorsData()
        first_use = agent.tool_uses - REMINDER_TOOL_USES
        is_reported = any(self.entries.use_lines(agent.session, nudge.key, first_use) for nudge in (ClientErrorsNudges.LOGGED, ClientErrorsNudges.UNHANDLED))
        return ClientErrorsData(count, is_reported)
