from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.merged_worker_task import MergedWorkerTask


class ReopenedWorkerTask(MergedWorkerTask):
    """The user reopened the task whose checked worker work was merged."""

    parent = MergedWorkerTask
    stack = (Ready,)

    def steps(self, story) -> None:
        story.user_did(f"/journal/tasks/{self.tasks.briefed}/reopen", {}, "user reopens the merged task").expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_task(self.tasks.briefed, state=TaskState.OPEN, delegated=False)
        story.expect_task_unheld(self.tasks.briefed)
        story.expect_stack(story.agents.main, Ready)
