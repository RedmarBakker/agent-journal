from journal.engine.nudger import NUDGE
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from tests.scenarios.builder.said_nudge import SaidNudge


class NudgeLog:
    """The lines the nudger gave the main environment's agents, read from its entries once the worker thread has settled, each step taking those said since the step before."""

    def __init__(self, app) -> None:
        self.app, self.seen = app, 0

    def since_last(self) -> tuple[SaidNudge, ...]:
        self.app.runtime().deferred.drain()
        with self.app.container.get(Scope).environment(self.app.container.get(Environments).lookup("main").id):
            entries = [entry for entry in reversed(self.app.container.get(Entries).kind_entries_scoped(1000)) if entry.entry_type == NUDGE]
        said, self.seen = entries[self.seen:], len(entries)
        return tuple(SaidNudge(entry.data["key"], entry.data.get("values", {})) for entry in said)
