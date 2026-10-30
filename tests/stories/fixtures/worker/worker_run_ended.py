from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


class WorkerRunEnded(StateFixture):
    """The worker that clocked out wrote its report and its run ended, its session kept to resume: story.agents.workers.first()."""

    stack = (Ready,)

    parent = WorkerDelivered

    def steps(self, story) -> None:
        story.worker_run_ends_with_its_session(story.agents.workers.first(), "the parser is done")

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.DELIVERED)
        story.expect_stack(story.agents.workers.first(), Void, Ended)
