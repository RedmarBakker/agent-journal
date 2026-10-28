from journal.models.task_state import TaskState
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class TaskInHand(StateFixture):
    """The agent at work has created the footer and started it, named to the story as scenario.task_in_hand."""

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        scenario.task_in_hand = scenario.agent_takes_a_task("the footer")

    def expected(self, scenario) -> None:
        scenario.expect_task(scenario.task_in_hand, state=TaskState.STARTED)
        scenario.expect_stack("idle", "working")
