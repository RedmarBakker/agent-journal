from journal.features.workers.support.allowed_models import AllowedModels
from journal.features.reviewing.support.review_links import ReviewLinks
from journal.features.reviewing.support.reviewer_runner import ReviewerRunner
from journal.models.reviewer import Reviewer
from journal.models.reviewer_state import ReviewerState
from journal.models.worker import Worker
from journal.providers.providers import Providers
from journal.repositories.reviewers import Reviewers
from journal.support.actor import Actor

JURAN = "Mr. Juran, keeper of the quality ledger"


class ReviewerDispatch:
    """Sends a reviewer, as the journal and never an agent: an idle one, in its own session with its memory of the reviews it made, on the strongest model the settings allow a reviewer, handed the work as its whole brief, linked to the worker whose work it reviews, and started by its own runner; and adds a reviewer, named after Juran, idle until it is sent."""

    def __init__(self, reviewers: Reviewers, links: ReviewLinks, runner: ReviewerRunner, providers: Providers, allowed: AllowedModels) -> None:
        self.reviewers, self.links, self.runner, self.providers, self.allowed = reviewers, links, runner, providers, allowed

    def sent(self, reviewer: Reviewer, worker: Worker, brief: str) -> Reviewer:
        reviewing = self.reviewers.save(reviewer.next_review(brief, self.model()), Actor.system())
        self.links.linked(reviewing, worker)
        return self.runner.start(reviewing, reviewer.session)

    def added(self, environment_id: int) -> Reviewer:
        return self.reviewers.save(Reviewer(environment_id=environment_id, name=JURAN, provider=self.providers.default().name, model=self.model(), state=ReviewerState.REVIEWED), Actor.system())

    def model(self) -> str:
        return self.allowed.strongest(self.providers.default().name, "reviewer")
