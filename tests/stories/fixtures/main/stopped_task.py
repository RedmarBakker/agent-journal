from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class StoppedTask(StateFixture):
    """The user wakes a stopped agent after ten quiet minutes, and the agent stopped with its task in hand: story.tasks.started."""

    stack = (Ready, Working)

    parent = StartedTask

    settings = ((TasksOptions.WAKE_MINUTES, 10),)

    def steps(self, story) -> None:
        story.agent_stops(story.agents.main)

    def expected(self, story) -> None:
        story.last_step.expect_refused(story.agents.main, TasksNudges.TASK_CONTINUATION)
