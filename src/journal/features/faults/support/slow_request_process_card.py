from journal.chat.process_card import ProcessCard
from journal.chat.process_cards import ProcessCards
from journal.models.message import Message
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class SlowRequestProcessCard(ProcessCard):
    """The process card of the slow requests: how many went over their budget, and the slowest routes with their worst time and count, a new mark in the chat each time the agent is told of them."""

    KEY = "slow:requests"
    name = "slow_request"

    def __init__(self, cards: ProcessCards, scope: Scope) -> None:
        self.cards, self.scope = cards, scope

    def show(self, total: int, data: dict, detail: str, moment: float) -> None:
        self.cards.show(self.name, self.scope.id, f"{self.KEY}:{int(moment)}", f"Slow requests report ready: {total} over budget, read it with journal developer slowest", data, Actor.system(), CardKind.FAULTS, False, detail)

    def refresh(self, message: Message) -> dict:
        return {"active": False}
