from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.models.saved import Saved
from journal.features.questions.support.question_process_card import QuestionProcessCard
from journal.models.question import Question


class QuestionCard(Listener[Saved]):
    """A question asked is a process card in the chat that points at it, settled in place when it is answered; the question stays a row of its own."""

    def __init__(self, card: QuestionProcessCard, cards: ProcessCards) -> None:
        self.card, self.cards = card, cards

    def handle(self, event: Saved) -> None:
        if isinstance(event.model, Question):
            self.cards.show(self.card.mark(event.model))
