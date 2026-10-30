from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.working_task import WorkingTask
from tests.stories.fixtures.worker.working_worker import WorkingWorker
from tests.stories.fixtures.state_fixture import StateFixture


class QueuedWorker(StateFixture):
    """The working worker has a second task, the docs, queued behind the one in its hands: story.tasks.queued."""

    stack = (Ready, ExternalWait)

    parent = WorkingWorker

    def steps(self, story) -> None:
        self.tasks.queued = story.agent_creates_task(story.agents.main, "the docs")
        story.agent_runs(story.agents.main, f"worker queue {story.agents.workers.first()} {self.tasks.queued}")

    def expected(self, story) -> None:
        story.expect_task(self.tasks.queued, delegated=True)
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)
