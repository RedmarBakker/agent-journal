from journal.features.tasks.states.choosing_paused_work import ChoosingPausedWork
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.task_queue import TaskQueue


class PausedWorkChoice(StateFixture):
    """In auto mode the agent paused the footer for the open header and stopped, so it is asked which to take up: start.started_task paused and start.next_open open."""

    stack = (Ready, ChoosingPausedWork)

    parent = TaskQueue

    def steps(self, story) -> None:
        story.user_sets(TasksOptions.AUTO, True)
        story.agent_runs(f"task pause {self.started_task} 'the header first'")
        story.agent_stops()

    def expected(self, story) -> None:
        story.expect_refused(TasksNudges.PAUSED_CHOICE)
        story.expect_stack(Ready, ChoosingPausedWork)
