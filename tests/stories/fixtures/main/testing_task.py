from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class TestingTask(StateFixture):
    """The agent put its task in testing, out of its hand until a test run says how it went: story.tasks.started."""

    stack = (Ready,)

    parent = StartedTask

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"task test {self.tasks.started}")

    def expected(self, story) -> None:
        story.expect_task(self.tasks.started, state=TaskState.TESTING)
