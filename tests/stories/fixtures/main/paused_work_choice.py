from journal.features.tasks.states.choosing_paused_work import ChoosingPausedWork
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.task_queue import TaskQueue


class PausedWorkChoice(StateFixture):
    """In auto mode the agent paused the footer for the open header and stopped, so it is asked which to take up: story.tasks.started paused and story.tasks.open open."""

    stack = (Ready, ChoosingPausedWork)

    parent = TaskQueue

    settings = ((TasksOptions.AUTO, True),)

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"task pause {self.tasks.started} 'the header first'")
        story.agent_stops(story.agents.main)

    def expected(self, story) -> None:
        story.expect_refused(story.agents.main, TasksNudges.PAUSED_CHOICE)
        story.expect_stack(story.agents.main, Ready, ChoosingPausedWork)
