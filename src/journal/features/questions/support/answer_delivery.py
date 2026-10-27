from datetime import datetime, timezone

from journal.support.actor import Actor
from journal.models.question import Question
from journal.repositories.questions import Questions
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


class AnswerDelivery:
    """The one place a question is answered or closed, from the command or the viewer: the row keeps the answer, or that the user closed it, and the chat shows a card; the agents waiting on it are released by their Waiting state when the row's event reaches them."""

    def __init__(self, questions: Questions, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.questions = questions

    def answer(self, question: Question, text: str, actor: Actor) -> Question:
        if question.is_answered():
            raise Rejection(f"question {question.id} is answered already")
        return self.questions.save(question.answered(text, self.time_source.moment().timestamp()), actor)

    def close(self, question: Question, actor: Actor) -> Question:
        if question.is_answered():
            raise Rejection(f"question {question.id} is settled already")
        return self.questions.save(question.closed(self.time_source.moment().timestamp()), actor)
