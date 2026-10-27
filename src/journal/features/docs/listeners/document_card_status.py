from journal.chat.process_cards import ProcessCards
from journal.chat.row_process_card import RowProcessCard
from journal.events.listener import Listener
from journal.events.models.updated import Updated
from journal.models.doc import Doc
from journal.repositories.agents import Agents
from journal.support.actor_type import ActorType


class DocumentCardStatus(Listener[Updated]):
    """A document's card in the chat changes in place from being written to ready, and back, when its status changes."""

    def __init__(self, agents: Agents, card: RowProcessCard, cards: ProcessCards) -> None:
        self.agents, self.card, self.cards = agents, card, cards

    def handle(self, event: Updated) -> None:
        doc = event.model
        if not isinstance(doc, Doc) or "unfinished" not in event.changed() or event.actor.actor_type != ActorType.AGENT:
            return
        contents = self.card.card_contents(self.agents.session_agent(event.actor.agent_session()).environment_id, doc, event.actor)
        if self.cards.is_shown(contents):
            self.cards.show(contents)
