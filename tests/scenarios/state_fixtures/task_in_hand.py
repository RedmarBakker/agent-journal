from journal.models.task_state import TaskState
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class TaskInHand(StateFixture):
    """The agent at work has created task 1, the footer, and started it."""

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        scenario.agent_runs("task create 'the footer' --start")

    def expected(self, scenario) -> None:
        scenario.expect_task(1, state=TaskState.STARTED)
        scenario.expect_stack("idle", "working")
