from journal.engine.states.ended import Ended
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class EndedTask(StateFixture):
    """The agent at work on its started task ended its session, which leaves the task started under Ended."""

    stack = (Ready, Working, Ended)

    parent = StartedTask

    def steps(self, story) -> None:
        story.agent_ends_the_session()

    def expected(self, story) -> None:
        story.expect_task(self.started_task, state=TaskState.STARTED)
        story.expect_stack(Ready, Working, Ended)
