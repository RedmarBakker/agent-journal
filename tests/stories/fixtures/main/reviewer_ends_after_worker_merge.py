from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork


class ReviewerEndsAfterWorkerMerge(ReviewerAtWork):
    """A worker merges its task while its reviewer is still running."""

    parent = ReviewerAtWork
    settings = ()

    def steps(self, story) -> None:
        with story.app.container.get(Scope).environment(1):
            workers = story.app.container.get(Workers)
            worker = workers.find(self.workers.first)
            workers.save(worker.review_ended(story.app.container.get(TimeSource).seconds(), "reviewed"), Actor.system())
        worker = story.agents.workers.first()
        for point in (1, 2):
            story.agent_runs(story.agents.main, f"worker check {worker} {point}").expect_command_passed()
        story.agent_runs(story.agents.main, f"worker merge {worker}").expect_command_passed()

