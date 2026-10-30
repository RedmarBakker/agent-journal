from journal.engine.safety_conduct import PANIC_REFUSAL_COUNT
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class HeldStops(StateFixture):
    """The agent with its task in hand stopped one time short of a dead loop, each stop held with the task to carry on: story.tasks.started."""

    stack = (Ready, Working)

    parent = StartedTask

    def steps(self, story) -> None:
        story.repeat(PANIC_REFUSAL_COUNT - 1, lambda: story.agent_stops(story.agents.main))

    def expected(self, story) -> None:
        story.last_step.expect_refused(story.agents.main, TasksNudges.TASK_CONTINUATION)
        story.expect_stack(story.agents.main, Ready, Working)
