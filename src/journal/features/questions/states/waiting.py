from dataclasses import dataclass

from journal.engine.nudge import Nudge
from journal.engine.states.wait import Wait
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.question_answered import QuestionAnswered
from journal.events.rows.question_closed import QuestionClosed
from journal.events.feature_data import FeatureData
from journal.features.questions.questions_nudges import QuestionsNudges
from journal.features.questions.questions_part import QuestionsPart


@dataclass(frozen=True)
class Waiting(Wait):
    """The agent asked the user a question. Idle is fine; the answer pops it and names the question to read, the user closing the question pops it saying so, a prompt from the user is the answer in other words, and beneath another state it pops on resume once its question is settled. Pushed by the questions conduct on QuestionAsked."""

    name = "waiting"
    title = "Waiting on a question"
    question_id: int = 0

    def question_number(self) -> int:
        return self.question_id

    def wait_description(self) -> tuple[str, str]:
        return f"your answer to question {self.question_id}", f"questions:{self.question_id}"

    def on_question_answered(self, event: QuestionAnswered, settings: Settings) -> Transition:
        return self.pop(QuestionsNudges.QUESTION_ANSWERED.create(n=event.question_id)) if event.question_id == self.question_id else self.none()

    def on_question_closed(self, event: QuestionClosed, settings: Settings) -> Transition:
        return self.pop(QuestionsNudges.QUESTION_CLOSED.create(n=event.question_id)) if event.question_id == self.question_id else self.none()

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...] | Transition:
        return () if self.question_id in data.part(QuestionsPart).open else self.pop(QuestionsNudges.QUESTION_ANSWERED.create(n=self.question_id))
