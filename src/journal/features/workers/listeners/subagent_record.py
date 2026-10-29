from journal.events.listener import Listener
from journal.events.models.updated import Updated
from journal.features.workers.support.subagent_entries import SubagentEntries
from journal.models.entry import Entry
from journal.models.subagent import Subagent
from journal.repositories.subagents import Subagents
from journal.support.actor import Actor

DISPATCH_PREFIX = "sub:"


class SubagentRecord(Listener[Updated]):
    """Each subagent the agent dispatched is a row, written as each entry that moves it is resolved with what the journal answered, so a dispatch the journal refused is never a row and the next hook counts the rows as they are; a retired subagent stays retired until it is sent a message; a row whose dispatch entry was trimmed is moved by the entry alone; a stop or a session's start or end with no subagent running moves nothing and pairs nothing; only the rows an entry can move are read, the running ones, the newest, and the one a message runs again, with the dispatches newer than the newest stored."""

    def __init__(self, entries: SubagentEntries, subagents: Subagents) -> None:
        self.entries, self.subagents = entries, subagents

    def handle(self, event: Updated) -> None:
        if not isinstance(event.model, Entry) or not SubagentEntries.is_dispatch_entry(event.model):
            return
        session = event.model.data.get("session_id", "")
        if SubagentEntries.is_end_entry(event.model) and not self.subagents.running_session_subagents(session):
            return
        stored = {s.dispatch: s for s in self.movable_rows(session, event.model)}
        newest = self.subagents.newest_session_subagent(session)
        paired = {row.dispatch: row for row in self.entries.rows(session) if row.dispatch in stored or not newest or self.number(row) > self.number(newest[0])}
        for row in paired.values():
            self.recorded(stored.get(row.dispatch), row, Actor.agent(session))
        for row in [row for dispatch, row in stored.items() if dispatch not in paired]:
            self.recorded(row, SubagentEntries.moved(row, event.model), Actor.agent(session))

    def movable_rows(self, session: str, entry: Entry) -> list[Subagent]:
        receiver = SubagentEntries.message_receiver(entry)
        return [*self.subagents.running_session_subagents(session), *self.subagents.newest_session_subagent(session), *self.subagents.session_subagent(session, receiver)]

    @staticmethod
    def number(row: Subagent) -> int:
        return int(row.dispatch.removeprefix(DISPATCH_PREFIX))

    def recorded(self, stored: Subagent | None, paired: Subagent, actor: Actor) -> None:
        if stored is None:
            self.subagents.save(paired, actor)
            return
        updated = stored.recorded(paired)
        if updated != stored:
            self.subagents.save(updated, actor)
