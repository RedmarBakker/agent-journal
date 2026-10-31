from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class LooseBlock(StateFixture):
    """The agent blocked the logo with nothing to end the block, then completed the task it had started, its first
    completed task, which names no block yet: story.tasks.loose."""

    stack = (Ready,)

    parent = StartedTask

    def steps(self, story) -> None:
        self.tasks.loose = story.agent_creates_task(story.agents.main, "the logo")
        story.agent_runs(story.agents.main, f"task block {self.tasks.loose} 'waits on the designer'")
        story.agent_runs(story.agents.main, f"task complete {self.tasks.started} --how done")

    def expected(self, story) -> None:
        story.last_step.expect_agent_not_told(story.agents.main, TasksNudges.LOOSE_BLOCKS)
        story.expect_task(self.tasks.loose, state=TaskState.BLOCKED)
        story.expect_stack(story.agents.main, Ready)
