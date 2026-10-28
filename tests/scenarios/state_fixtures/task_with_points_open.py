from journal.models.task_state import TaskState
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.builder.stack_states import IDLE
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class TaskWithPointsOpen(StateFixture):
    """The agent at work has filed the parser, open, its brief two points a worker proves, named to the story as scenario.open_task."""

    stack = (IDLE,)

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        scenario.provide(TaskWithPointsOpen, "open_task", scenario.agent_creates_task("the parser", "- reads the grammar\n- names each rule"))

    def expected(self, scenario) -> None:
        scenario.expect_task(scenario.open_task, state=TaskState.OPEN)
