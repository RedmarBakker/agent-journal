from journal.engine.engine_nudges import EngineNudges
from journal.engine.safety_conduct import PANIC_REFUSAL_COUNT
from journal.engine.states.panicking import Panicking
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class LoopedStops(StateFixture):
    """The agent with its task in hand stopped again and again, each stop held, until the loop was named and Panicking pushed."""

    stack = (Ready, Working, Panicking)

    parent = StartedTask

    def steps(self, story) -> None:
        story.repeat(PANIC_REFUSAL_COUNT, story.agent_stops)

    def expected(self, story) -> None:
        story.expect_agent_told(EngineNudges.STOP_LOOP)
        story.expect_stack(Ready, Working, Panicking)
