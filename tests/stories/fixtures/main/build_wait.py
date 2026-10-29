from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.task_queue import TaskQueue


class BuildWait(StateFixture):
    """The agent with the footer in hand and the header open waits on the build: story.tasks.started and story.tasks.open."""

    stack = (Ready, Working, ExternalWait)

    parent = TaskQueue

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, "await 'the build' --until false")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready, Working, ExternalWait)
