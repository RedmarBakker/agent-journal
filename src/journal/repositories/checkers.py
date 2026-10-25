from typing import TypeVar

from journal.models.helper import Helper
from journal.repositories.scoped_repository import ScopedRepository

H = TypeVar("H", bound=Helper)


class Checkers(ScopedRepository[H]):
    """The rows of the agents the journal sends itself to check work, the verifiers or the reviewers: the one working in a session, and the one of a number in any environment."""

    def session_checkers(self, session: str) -> list[H]:
        return self.selected_globally(self.query().filter(session=session).order("id")) if session else []

    def numbered(self, number: int) -> list[H]:
        return self.global_matching(id=number)
