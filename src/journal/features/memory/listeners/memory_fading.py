from journal.events.agent.compacting import Compacting
from journal.events.agent_listener import AgentListener
from journal.chat.moment_cards import MomentCards
from journal.features.memory.support.memory_owners import MemoryOwners
from journal.repositories.agents import Agents
from journal.repositories.memories import Memories
from journal.support.card_type import CardType
from journal.repositories.scope import Scope
from journal.support.actor import Actor


class MemoryFading(AgentListener[Compacting]):
    """A compaction of an agent, the main agent or a worker, lowers every one of its own memories still shown by one, as the system, and says so in one card in the chat; a subagent's compaction fades none."""

    def __init__(self, memories: Memories, owners: MemoryOwners, agents: Agents, scope: Scope, cards: MomentCards) -> None:
        self.memories, self.owners, self.agents, self.scope, self.cards = memories, owners, agents, scope, cards

    def handle(self, event: Compacting) -> None:
        if event.subagent:
            return
        with self.scope.environment(event.environment_id):
            lowered_memories = self.memories.fade_all(self.owners.agent_owner(self.agents.session_agent(event.session)), Actor.system())
        if lowered_memories:
            visible_count = len([memory for memory in lowered_memories if memory.is_visible()])
            self.cards.show(event.environment_id, event.session, f"Memories faded by one: {visible_count} of {len(lowered_memories)} still shown", "", shows=CardType.MEMORIES)
