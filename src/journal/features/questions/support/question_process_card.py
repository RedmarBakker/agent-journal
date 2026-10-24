from journal.chat.process_card import ProcessCard
from journal.chat.process_mark import ProcessMark
from journal.models.message import Message
from journal.models.question import Question
from journal.repositories.questions import Questions
from journal.support.card_kind import CardKind


class QuestionProcessCard(ProcessCard):
    """The process card of a question asked, open with its options until it is answered and then showing the answer."""

    name = "question"

    def __init__(self, questions: Questions) -> None:
        self.questions = questions

    def card_contents(self, question: Question) -> ProcessMark:
        data = {"kind": "question", "row": f"questions:{question.id}", "n": question.id, "options": list(question.options), "answer": question.answer}
        return ProcessMark(self.name, question.environment_id, f"question:{question.id}", question.text, data, question.creation_actor, CardKind.QUESTIONS, not question.is_answered(), session=question.creation_actor.id)

    def refresh(self, message: Message) -> dict:
        question = self.questions.find(message.data["n"])
        return {"answer": question.answer, "active": not question.is_answered()}
