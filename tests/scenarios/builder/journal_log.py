from journal.engine.nudger import NUDGE
from journal.engine.support.stack_history import StackHistory
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from tests.scenarios.builder.said_nudge import SaidNudge


class JournalLog:
    """What the journal did in the main environment since the step before, read from its entries once the worker thread has settled: the lines the nudger gave, by key and values, and each move of a stack as a path step, the top before, the top after and its cause."""

    def __init__(self, app) -> None:
        self.app, self.seen = app, 0

    def since_last(self) -> tuple[tuple[SaidNudge, ...], tuple[str, ...]]:
        self.app.runtime().deferred.drain()
        with self.app.container.get(Scope).environment(self.app.container.get(Environments).lookup("main").id):
            entries = [entry for entry in reversed(self.app.container.get(Entries).kind_entries_scoped(1000)) if entry.entry_type in (NUDGE, StackHistory.KIND)]
        fresh, self.seen = entries[self.seen:], len(entries)
        said = tuple(SaidNudge(entry.data["key"], entry.data.get("values", {})) for entry in fresh if entry.entry_type == NUDGE)
        steps = tuple(self.step(entry) for entry in fresh)
        return said, steps

    @staticmethod
    def step(entry) -> str:
        if entry.entry_type == NUDGE:
            return f"said {entry.data['key']}"
        before, after = entry.data.get("before") or [{}], entry.data.get("after") or [{}]
        return f"{before[-1].get('state', '')} > {after[-1].get('state', '')} on {entry.data.get('cause', '')}"
