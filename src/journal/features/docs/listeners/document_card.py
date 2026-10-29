from journal.chat.process_cards import ProcessCards
from journal.chat.row_process_card import RowProcessCard
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.models.doc import Doc
from journal.repositories.agents import Agents
from journal.support.agent_actor import AgentActor
from journal.support.subagent_actor import SubagentActor

class DocumentCard(Listener[Created]):
    """A document an agent writes is a mark in its environment's chat."""

    actors = (AgentActor, SubagentActor)

    def __init__(self, agents: Agents, card: RowProcessCard, cards: ProcessCards) -> None:
        self.agents, self.card, self.cards = agents, card, cards

    def handle(self, event: Created) -> None:
        doc = event.model
        if not isinstance(doc, Doc):
            return
        self.cards.show(self.card.card_contents(self.agents.session_agent(event.actor.agent_session()).environment_id, doc, event.actor))
