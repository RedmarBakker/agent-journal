from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker import SILENCE
from tests.stories.fixtures.worker.working_worker import WorkingWorker
from tests.stories.fixtures.state_fixture import StateFixture


class SilentWorker(StateFixture):
    """The clocked-in worker stayed quiet for its whole span: it was told to log, and the agent that sent it was told nothing yet."""

    stack = (Ready, ExternalWait)

    parent = WorkingWorker

    def steps(self, story) -> None:
        story.worker_is_quiet_past(SILENCE.amount)

    def expected(self, story) -> None:
        story.expect_worker_told(self.worker, WorkersNudges.WORKER_LOG_DUE)
        story.expect_main_not_told(WorkersNudges.SILENT_WORKER)
