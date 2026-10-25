from journal.engine.support.lazy_facts import LazyFacts
from journal.models.agent import Agent
from journal.repositories.reviewers import Reviewers
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.stage_times import StageTimes


class ReviewingDataReader:
    """Reads the reviewing feature's part of the feature data for an agent, each fact only when a listener asks for it."""

    def __init__(self, workers: Workers, reviewers: Reviewers, scope: Scope, stages: StageTimes) -> None:
        self.workers, self.reviewers, self.scope, self.stages = workers, reviewers, scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("reviewing", {
            "waiting_reviews": lambda: len(self.workers.queued_reviews()),
            "reviewers": lambda: len(self.reviewers.active()),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)
