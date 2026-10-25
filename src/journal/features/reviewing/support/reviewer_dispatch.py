from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.reviewing.support.review_links import ReviewLinks
from journal.features.reviewing.support.reviewer_runner import ReviewerRunner
from journal.models.reviewer import Reviewer
from journal.models.reviewer_state import ReviewerState
from journal.models.worker import Worker
from journal.providers.providers import Providers
from journal.repositories.reviewers import Reviewers
from journal.support.actor import Actor

JURAN = "Mr. Juran, keeper of the quality ledger"
# the profile whose model a reviewer runs on, the strongest, since it critiques code against the project's rules; its instructions are not given, since the brief is the reviewer's whole instruction
MODEL_PROFILE = "journal-senior"


class ReviewerDispatch:
    """Sends a reviewer, as the journal and never an agent: an idle one, in its own session with its memory of the reviews it made, handed the work as its whole brief, linked to the worker whose work it reviews, and started by its own runner; and adds a reviewer, named after Juran, idle until it is sent."""

    def __init__(self, reviewers: Reviewers, links: ReviewLinks, runner: ReviewerRunner, providers: Providers, profiles: ProfileFiles) -> None:
        self.reviewers, self.links, self.runner, self.providers, self.profiles = reviewers, links, runner, providers, profiles

    def sent(self, reviewer: Reviewer, worker: Worker, brief: str) -> Reviewer:
        reviewing = self.reviewers.save(reviewer.next_review(brief), Actor.system())
        self.links.linked(reviewing, worker)
        return self.runner.start(reviewing, reviewer.session)

    def added(self, environment_id: int) -> Reviewer:
        provider = self.providers.default()
        return self.reviewers.save(Reviewer(environment_id=environment_id, name=JURAN, provider=provider.name, model=provider.profile_model(self.profiles.read(MODEL_PROFILE)), state=ReviewerState.REVIEWED), Actor.system())
