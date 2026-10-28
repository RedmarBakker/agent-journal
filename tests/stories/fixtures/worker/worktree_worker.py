from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.working_task import WorkingTask
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.briefed_task import BriefedTask
from tests.stories.fixtures.state_fixture import StateFixture


class WorktreeWorker(StateFixture):
    """The project is a throwaway git repository in the story's own temp folder; the agent sent a worker with a worktree of its own on the briefed task and it clocked in: start.worker."""

    stack = (Ready, ExternalWait)

    parent = BriefedTask

    def steps(self, story) -> None:
        story.project_is_a_git_repository()
        self.worker = story.agent_dispatches_worktree_worker("Lady Lovelace", self.briefed)
        story.worker_session_starts(self.worker)
        story.worker_clocks_in(self.worker)

    def expected(self, story) -> None:
        story.expect_worker(self.worker, state=WorkerState.READY)
        story.expect_worker_stack(self.worker, Void, WorkingTask)
