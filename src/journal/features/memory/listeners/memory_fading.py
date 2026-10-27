from journal.events.agent.compacting import Compacting
from journal.events.agent_listener import AgentListener
from journal.chat.moment_cards import MomentCards
from journal.repositories.memories import Memories
from journal.support.card_type import CardType
from journal.repositories.scope import Scope
from journal.support.actor import Actor


class MemoryFading(AgentListener[Compacting]):
    """A compaction of the environment's agent lowers every memory still shown by one, as the system, and says so in one card in the chat."""

    def __init__(self, memories: Memories, scope: Scope, cards: MomentCards) -> None:
        self.memories, self.scope, self.cards = memories, scope, cards

    def handle(self, event: Compacting) -> None:
        if event.subagent:
            return
        with self.scope.environment(event.environment_id):
            lowered_memories = self.memories.fade_all(Actor.system())
        if lowered_memories:
            visible_count = len([memory for memory in lowered_memories if memory.is_visible()])
            self.cards.show(event.environment_id, event.session, f"Memories faded by one: {visible_count} of {len(lowered_memories)} still shown", "", shows=CardType.MEMORIES)
