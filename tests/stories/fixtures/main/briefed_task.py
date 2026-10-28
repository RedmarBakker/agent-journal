from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class BriefedTask(StateFixture):
    """The agent at work has filed the parser, open, its brief two points a worker proves, named to the story as start.briefed."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.briefed = story.agent_creates_briefed_task("the parser", "- reads the grammar\n- names each rule")

    def expected(self, story) -> None:
        story.expect_task(self.briefed, state=TaskState.OPEN)
