from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.question_closed import QuestionClosed
from journal.models.support.ref import Ref
from journal.support.actor import Actor
from journal.support.card_type import CardType


class CloseCard(Listener[QuestionClosed]):
    """A question the user closed without an answer is one mark in the chat saying so."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: QuestionClosed) -> None:
        self.cards.show(event.environment_id, "", f"You closed question {event.question_id} without an answer", "", Ref("questions", event.question_id), actor=Actor.parse(event.actor), shows=CardType.QUESTIONS)
