from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.rows.question_answered import QuestionAnswered
from journal.models.support.ref import Ref
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class AnswerCard(Listener[QuestionAnswered]):
    """A question answered, by the user or by another, is one mark in the chat saying who answered it."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: QuestionAnswered) -> None:
        actor = Actor.parse(event.actor)
        label = f"You answered question {event.question_id}" if actor.is_user() else f"Question {event.question_id} answered by {actor.lookup}"
        self.cards.show(event.environment_id, "", label, "", Ref("questions", event.question_id), actor=actor, shows=CardKind.QUESTIONS)
