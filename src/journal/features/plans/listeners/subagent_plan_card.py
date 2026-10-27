from journal.chat.process_cards import ProcessCards
from journal.chat.row_process_card import RowProcessCard
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.models.plan import Plan


class SubagentPlanCard(Listener[Created]):
    """A plan a subagent creates is a card in the chat of the agent that sent it, among that subagent's other marks."""

    def __init__(self, card: RowProcessCard, cards: ProcessCards) -> None:
        self.card, self.cards = card, cards

    def handle(self, event: Created) -> None:
        plan = event.model
        if isinstance(plan, Plan) and event.actor.is_subagent():
            self.cards.show(self.card.card_contents(plan.environment_id, plan, event.actor))
