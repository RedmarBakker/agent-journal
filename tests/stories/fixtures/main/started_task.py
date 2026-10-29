from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class StartedTask(StateFixture):
    """The agent at work has created the footer and started it, named to the story as story.tasks.started."""

    stack = (Ready, Working)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.tasks.started = story.agent_takes_a_task(story.agents.main, "the footer")

    def expected(self, story) -> None:
        story.expect_task(self.tasks.started, state=TaskState.STARTED)
        story.expect_stack(story.agents.main, Ready, Working)
