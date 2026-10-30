from datetime import datetime, timezone

from journal.events.agent.compacting import Compacting
from journal.events.agent_listener import AgentListener
from journal.chat.moment_cards import MomentCards
from journal.features.memory.support.closed_rows import ClosedRows
from journal.features.memory.support.memory_owners import MemoryOwners
from journal.models.memory import Memory
from journal.models.support.ref import Ref
from journal.repositories.memories import Memories
from journal.repositories.messages import Messages
from journal.support.card_type import CardType
from journal.repositories.scope import Scope
from journal.support.actor import Actor

ROUND = "round"


class MemoryFading(AgentListener[Compacting]):
    """A compaction of an agent, the main agent or a worker, removes the memories tied to a task or plan that is closed, then lowers every one of its own memories still shown by one, as the system, and says so in one card in the chat that keeps the round: each memory still shown and each faded to nought with its weight before and after, and each removed since the last round; a subagent's compaction fades none."""

    def __init__(self, memories: Memories, owners: MemoryOwners, scope: Scope, cards: MomentCards, messages: Messages, closed_rows: ClosedRows) -> None:
        self.memories, self.owners, self.scope, self.cards, self.messages, self.closed_rows = memories, owners, scope, cards, messages, closed_rows

    def handle(self, event: Compacting) -> None:
        if event.subagent:
            return
        with self.scope.environment(event.environment_id):
            owner = self.owners.agent_owner(event.agent)
            self.ended(owner, event.time)
            lowered_memories = self.memories.fade_all(owner, Actor.system())
            removed = self.memories.removed_recent(owner, self.last_round_at(event.session))
        if lowered_memories:
            visible_count = len([memory for memory in lowered_memories if memory.is_visible()])
            self.cards.show_fields(event.environment_id, event.session, f"Memories faded by one: {visible_count} of {len(lowered_memories)} still shown", {"kind": "card", "outcome": "", "row": "", "command": "", ROUND: memory_round(lowered_memories, removed)}, Actor.system(), CardType.MEMORIES)

    def ended(self, owner: Ref | None, time: float) -> None:
        for memory in self.memories.tied(owner):
            if self.closed_rows.closed_state(Ref.parse(memory.expiry_row)):
                self.memories.save(memory.removed(datetime.fromtimestamp(time, timezone.utc)), Actor.system())

    def last_round_at(self, session: str) -> datetime | None:
        latest = self.messages.newest_session_moment(str(CardType.MEMORIES), session, ROUND)
        return latest.created_at if latest else None


def memory_round(lowered: list[Memory], removed: list[Memory]) -> dict:
    entry = lambda memory: {"id": memory.id, "text": memory.text, "weight_before": memory.weight + 1, "weight_after": memory.weight}
    return {
        "shown": [entry(memory) for memory in lowered if memory.is_visible()],
        "faded": [entry(memory) for memory in lowered if not memory.is_visible()],
        "removed": [{"id": memory.id, "text": memory.text, "weight": memory.weight, "end_reason": memory.end_reason()} for memory in removed],
    }
