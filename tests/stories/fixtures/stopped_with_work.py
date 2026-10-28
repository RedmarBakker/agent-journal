from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from tests.stories.fixtures.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class StoppedWithWork(StateFixture):
    """The user wakes a stopped agent after ten quiet minutes, and the agent stopped with its task in hand: start.started_task."""

    stack = (Ready, Working)

    parent = StartedTask

    def steps(self, story) -> None:
        story.user_sets(TasksOptions.WAKE_MINUTES, 10)
        story.agent_stops()

    def expected(self, story) -> None:
        story.expect_refused(TasksNudges.TASK_CONTINUATION)
