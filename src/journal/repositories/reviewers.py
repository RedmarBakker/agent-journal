from journal.models.reviewer import Reviewer
from journal.models.reviewer_state import ReviewerState
from journal.repositories.scoped_repository import ScopedRepository


class Reviewers(ScopedRepository[Reviewer]):
    model = Reviewer

    def session_reviewer(self, session: str) -> list[Reviewer]:
        return self.selected_globally(self.query().filter(session=session).order("id")) if session else []

    def numbered(self, number: int) -> list[Reviewer]:
        return self.global_matching(id=number)

    def idle(self) -> list[Reviewer]:
        return self.newest(self.query().filter(state=ReviewerState.REVIEWED).limit(1))
