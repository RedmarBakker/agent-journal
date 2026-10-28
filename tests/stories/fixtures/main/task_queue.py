from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class TaskQueue(StateFixture):
    """The agent works on the footer with the header filed after it, still open: start.started_task and start.next_open."""

    stack = (Ready, Working)

    parent = StartedTask

    def steps(self, story) -> None:
        self.next_open = story.agent_creates_task("the header")

    def expected(self, story) -> None:
        story.expect_task(self.next_open, state=TaskState.OPEN)
        story.expect_task(self.started_task, state=TaskState.STARTED)
