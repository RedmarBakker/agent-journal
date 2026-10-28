from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.agent_at_work import AgentAtWork
from tests.stories.fixtures.state_fixture import StateFixture


class TaskInHand(StateFixture):
    """The agent at work has created the footer and started it, named to the story as start.task_in_hand."""

    stack = (Ready, Working)

    builds_on = AgentAtWork

    def steps(self, story) -> None:
        self.task_in_hand = story.agent_takes_a_task("the footer")

    def expected(self, story) -> None:
        story.expect_task(self.task_in_hand, state=TaskState.STARTED)
        story.expect_stack(Ready, Working)
