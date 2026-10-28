from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class StartedTask(StateFixture):
    """The agent at work has created the footer and started it, named to the story as start.started_task."""

    stack = (Ready, Working)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.started_task = story.agent_takes_a_task("the footer")

    def expected(self, story) -> None:
        story.expect_task(self.started_task, state=TaskState.STARTED)
        story.expect_stack(Ready, Working)
