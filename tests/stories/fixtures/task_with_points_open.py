from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from tests.stories.fixtures.agent_at_work import AgentAtWork
from tests.stories.fixtures.state_fixture import StateFixture


class TaskWithPointsOpen(StateFixture):
    """The agent at work has filed the parser, open, its brief two points a worker proves, named to the story as start.open_task."""

    stack = (Ready,)

    builds_on = AgentAtWork

    def steps(self, story) -> None:
        self.open_task = story.agent_creates_task("the parser", "- reads the grammar\n- names each rule")

    def expected(self, story) -> None:
        story.expect_task(self.open_task, state=TaskState.OPEN)
