from journal.db.query import Query
from journal.features.suggestions.support.suggestion_search import SuggestionSearch
from journal.http.controllers.controller import Controller
from journal.http.support.request import Request
from journal.models.suggestion import Suggestion
from journal.models.suggestion_answer import SuggestionAnswer
from journal.repositories.suggestions import Suggestions
from journal.support.response import Response


class SuggestionController(Controller[Suggestion]):
    """The journal's suggestions, each answered once by the user: accepted, it names the page where the user finishes it."""

    def __init__(self, suggestions: Suggestions, suggesting: SuggestionSearch) -> None:
        self.repository, self.suggesting = suggestions, suggesting

    def open_rows(self, query: Query) -> Query:
        return query.filter_null("answer")

    def closed_rows(self, query: Query) -> Query:
        return query.filter_present("answer")

    def accept(self, request: Request) -> Response:
        return self.answered(request, SuggestionAnswer.ACCEPTED)

    def decline(self, request: Request) -> Response:
        return self.answered(request, SuggestionAnswer.DECLINED)

    def answered(self, request: Request, answer: SuggestionAnswer) -> Response:
        route = self.suggesting.answer(self.repository.find(request.number("id")), answer, request.actor)
        return Response.json({"answer": answer, "go": route})
