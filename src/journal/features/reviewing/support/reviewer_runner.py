import time

from journal.config import Config
from journal.features.reviewing.support.review_links import ReviewLinks
from journal.models.reviewer import Reviewer
from journal.models.support.ref import Ref
from journal.providers.providers import Providers
from journal.providers.support.helper_runner import HelperRunner
from journal.providers.support.helper_setup import HelperSetup
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.reviewers import Reviewers
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.time_source import TimeSource

REVIEWER_SECONDS = 1200


class ReviewerRunner(HelperRunner[Reviewer]):
    """Runs a reviewer the journal sent, for twenty minutes at most, time enough to run the tests the proofs name; a reviewer that ends without its report, or runs past its limit, first hands the work it reviews back to the agent that sent the worker, for that agent's own check, so the work is never left waiting on it, and the reviewer ends even when that fails."""

    seconds = REVIEWER_SECONDS

    def __init__(self, config: Config, providers: Providers, setup: HelperSetup, reviewers: Reviewers, environments: Environments, agents: Agents, scope: Scope, workers: Workers, tasks: Tasks, links: ReviewLinks, time_source: TimeSource) -> None:
        super().__init__(config, providers, setup, reviewers, environments, agents, scope, time_source)
        self.workers, self.tasks, self.links = workers, tasks, links

    def ended(self, reviewer: Reviewer) -> None:
        try:
            with self.rows.writing():
                current = self.rows.find(reviewer.row_id)
                if current.is_reviewing():
                    self.return_work(current)
        finally:
            super().ended(reviewer)

    def return_work(self, reviewer: Reviewer) -> None:
        worker = self.workers.find(self.links.worker(reviewer).id)
        if worker.review_pending:
            self.workers.save(worker.review_failed(self.time_source.seconds(), self.tasks.last_task_id(Ref.build(worker))), Actor.system())
