from journal.models.reviewer import Reviewer
from journal.models.reviewer_state import ReviewerState
from journal.repositories.checkers import Checkers


class Reviewers(Checkers[Reviewer]):
    model = Reviewer

    def idle(self) -> list[Reviewer]:
        return self.newest(self.query().filter(state=ReviewerState.REVIEWED).limit(1))
