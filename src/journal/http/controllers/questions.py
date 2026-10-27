from journal.db.query import Query
from journal.features.questions.support.answer_delivery import AnswerDelivery
from journal.http.controllers.controller import Controller
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.question import Question
from journal.repositories.questions import Questions


class QuestionController(Controller[Question]):
    """The agent's questions; one is open until the user answers it or closes it, no longer needed, which each row says."""

    def __init__(self, questions: Questions, respondent: AnswerDelivery) -> None:
        self.repository, self.answering = questions, respondent

    def shown_page(self, rows: list[Question]) -> list[dict]:
        return [{**ModelFields.build(question), "closed": question.is_closed()} for question in rows]

    def index_page(self, rows: list[Question]) -> list[dict]:
        return self.shown_page(rows)

    def open_rows(self, query: Query) -> Query:
        return query.filter_null("answer")

    def closed_rows(self, query: Query) -> Query:
        return query.filter_present("answer")

    def answer(self, request: Request) -> Response:
        return Response.json(self.answering.answer(self.repository.find(request.number("id")), request.body.get("answer", ""), request.actor))

    def close(self, request: Request) -> Response:
        return Response.json(self.shown(self.answering.close(self.repository.find(request.number("id")), request.actor)))
