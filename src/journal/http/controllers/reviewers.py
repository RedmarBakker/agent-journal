from journal.db.query import Query
from journal.features.reviewing.support.review_links import REVIEWS
from journal.http.controllers.controller import Controller
from journal.http.support.model_fields import ModelFields
from journal.models.reviewer import Reviewer
from journal.models.reviewer_state import ReviewerState
from journal.repositories.links import Links
from journal.repositories.reviewers import Reviewers


class ReviewerController(Controller[Reviewer]):
    """The reviewers the journal sent here; one that ended without a report is closed. Each names the workers whose work it reviewed, in order."""

    repository: Reviewers

    def __init__(self, reviewers: Reviewers, links: Links) -> None:
        self.repository, self.links = reviewers, links

    def open_rows(self, query: Query) -> Query:
        return query.filter_unequal("state", ReviewerState.ENDED)

    def closed_rows(self, query: Query) -> Query:
        return query.filter(state=ReviewerState.ENDED)

    def shown_page(self, rows: list[Reviewer]) -> list[dict]:
        return [{**ModelFields.build(row), "reviewed": [str(ref) for ref in self.links.targets(row, REVIEWS)]} for row in rows]
