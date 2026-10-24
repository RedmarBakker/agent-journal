from journal.models.verifier import Verifier
from journal.repositories.scoped_repository import ScopedRepository


class Verifiers(ScopedRepository[Verifier]):
    model = Verifier

    def session_verifier(self, session: str) -> list[Verifier]:
        return self.selected_globally(self.query().filter(session=session).order("id")) if session else []

    def numbered(self, number: int) -> list[Verifier]:
        return self.global_matching(id=number)
