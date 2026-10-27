from datetime import datetime

from journal.events.agent.compacting import Compacting
from journal.events.agent_listener import AgentListener
from journal.chat.moment_cards import MomentCards
from journal.features.memory.support.memory_owners import MemoryOwners
from journal.repositories.agents import Agents
from journal.models.memory import Memory
from journal.repositories.memories import Memories
from journal.repositories.messages import Messages
from journal.support.card_type import CardType
from journal.repositories.scope import Scope
from journal.support.actor import Actor

ROUND = "round"
ROUNDS_LOOKED_BACK = 50


class MemoryFading(AgentListener[Compacting]):
    """A compaction of an agent, the main agent or a worker, lowers every one of its own memories still shown by one, as the system, and says so in one card in the chat that keeps the round: each memory still shown and each faded to nought with its weight before and after, and each removed since the last round; a subagent's compaction fades none."""

    def __init__(self, memories: Memories, owners: MemoryOwners, agents: Agents, scope: Scope, cards: MomentCards, messages: Messages) -> None:
        self.memories, self.owners, self.agents, self.scope, self.cards, self.messages = memories, owners, agents, scope, cards, messages

    def handle(self, event: Compacting) -> None:
        if event.subagent:
            return
        with self.scope.environment(event.environment_id):
            owner = self.owners.agent_owner(self.agents.session_agent(event.session))
            lowered_memories = self.memories.fade_all(owner, Actor.system())
            removed = self.memories.removed_since(owner, self.last_round_at(event.session))
        if lowered_memories:
            visible_count = len([memory for memory in lowered_memories if memory.is_visible()])
            self.cards.show_fields(event.environment_id, event.session, f"Memories faded by one: {visible_count} of {len(lowered_memories)} still shown", {"kind": "card", "outcome": "", "row": "", "command": "", ROUND: memory_round(lowered_memories, removed)}, Actor.system(), CardType.MEMORIES)

    def last_round_at(self, session: str) -> datetime | None:
        return next((message.created_at for message in self.messages.newest_moments((str(CardType.MEMORIES),), ROUNDS_LOOKED_BACK) if ROUND in message.data and message.session == session), None)


def memory_round(lowered: list[Memory], removed: list[Memory]) -> dict:
    entry = lambda memory: {"id": memory.id, "text": memory.text, "weight_before": memory.weight + 1, "weight_after": memory.weight}
    return {
        "shown": [entry(memory) for memory in lowered if memory.is_visible()],
        "faded": [entry(memory) for memory in lowered if not memory.is_visible()],
        "removed": [{"id": memory.id, "text": memory.text, "weight": memory.weight, "end_reason": memory.end_reason()} for memory in removed],
    }
