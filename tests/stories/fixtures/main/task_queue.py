from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class TaskQueue(StateFixture):
    """The agent works on the footer with the header filed after it, still open: story.tasks.started and story.tasks.open."""

    stack = (Ready, Working)

    parent = StartedTask

    def steps(self, story) -> None:
        self.tasks.open = story.agent_creates_task(story.agents.main, "the header")

    def expected(self, story) -> None:
        story.expect_task(self.tasks.open, state=TaskState.OPEN)
        story.expect_task(self.tasks.started, state=TaskState.STARTED)
