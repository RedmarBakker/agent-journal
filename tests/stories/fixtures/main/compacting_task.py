from journal.engine.states.compacting import Compacting
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class CompactingTask(StateFixture):
    """The agent at work on its started task began a compaction, and the session has not started again yet."""

    stack = (Ready, Working, Compacting)

    parent = StartedTask

    def steps(self, story) -> None:
        story.compaction_begins()

    def expected(self, story) -> None:
        story.expect_stack(Ready, Working, Compacting)
