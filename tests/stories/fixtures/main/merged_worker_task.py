from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


class MergedWorkerTask(StateFixture):
    """The main agent checked both points and merged the worker's completed task."""

    parent = WorkerDelivered
    stack = (Ready,)

    def steps(self, story) -> None:
        worker = story.agents.workers.first()
        story.agent_runs(story.agents.main, f"worker check {worker} 1").expect_command_passed()
        story.agent_runs(story.agents.main, f"worker check {worker} 2").expect_command_passed()
        story.agent_runs(story.agents.main, f"worker merge {worker}").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_task(self.tasks.briefed, state=TaskState.COMPLETED)
        story.expect_stack(story.agents.main, Ready)
