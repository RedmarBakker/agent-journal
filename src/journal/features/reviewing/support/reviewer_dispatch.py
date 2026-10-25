from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.reviewing.support.reviewer_runner import ReviewerRunner
from journal.models.link import Link
from journal.models.reviewer import Reviewer
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.providers.providers import Providers
from journal.repositories.links import Links
from journal.repositories.reviewers import Reviewers
from journal.support.actor import Actor
from journal.support.rejection import Rejection

REVIEWS = "reviews"
JURAN = "Mr. Juran, keeper of the quality ledger"
# the profile whose model a reviewer runs on, the strongest, since it critiques code against the project's rules; its instructions are not given, since the brief is the reviewer's whole instruction
MODEL_PROFILE = "journal-senior"


class ReviewerDispatch:
    """Sends a reviewer, as the journal and never an agent: the idle one that reviewed last, in its own session with its memory of that review, else a new one named after Juran, handed the work as its whole brief, linked to the worker whose work it reviews, and started by its own runner; and finds the worker a reviewer reviews now, the last it was linked to."""

    def __init__(self, reviewers: Reviewers, links: Links, runner: ReviewerRunner, providers: Providers, profiles: ProfileFiles) -> None:
        self.reviewers, self.links, self.runner, self.providers, self.profiles = reviewers, links, runner, providers, profiles

    def sent(self, worker: Worker, brief: str) -> Reviewer:
        idle = self.reviewers.idle()
        if idle:
            return self.reviewing(idle[0].next_review(brief), worker, idle[0].session)
        provider = self.providers.default()
        return self.reviewing(Reviewer(environment_id=worker.environment_id, name=JURAN, brief=brief, provider=provider.name, model=provider.profile_model(self.profiles.read(MODEL_PROFILE))), worker, "")

    def reviewing(self, reviewer: Reviewer, worker: Worker, resume: str) -> Reviewer:
        reviewer = self.reviewers.save(reviewer, Actor.system())
        self.links.save(Link(source=Ref.build(reviewer), target=Ref.build(worker), kind=REVIEWS), Actor.system())
        return self.runner.start(reviewer, resume)

    def reviewed(self, number: int) -> Ref:
        targets = self.links.targets(self.reviewers.find(number), REVIEWS)
        if not targets:
            raise Rejection(f"reviewer {number} reviews nothing: only a reviewer the journal sent gives a review")
        return targets[-1]
