from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.task_queue import TaskQueue


class AwaitWithOpenWork(StateFixture):
    """The agent with the footer in hand and the header open waits on the build: start.started_task and start.next_open."""

    stack = (Ready, Working, ExternalWait)

    parent = TaskQueue

    def steps(self, story) -> None:
        story.agent_runs("await 'the build' --until false")

    def expected(self, story) -> None:
        story.expect_stack(Ready, Working, ExternalWait)
