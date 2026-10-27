from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.state_fixtures.agent_at_work import AgentAtWork
from tests.state_fixtures.state_fixture import StateFixture


class PlanJustStarted(StateFixture):
    """The user made plan 1 with one task, readied and approved it, and the agent at work started it, so task 1 is in hand under the plan."""

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        scenario.user_runs("plan create p --brief b")
        scenario.user_runs("plan add 1 first")
        scenario.user_runs("plan ready 1")
        scenario.user_runs("plan approve 1")
        scenario.agent_runs("plan start 1")

    def expected(self, scenario) -> None:
        scenario.expect_plan(1, state=PlanState.STARTED)
        scenario.expect_task(1, state=TaskState.STARTED)
        scenario.expect_stack("idle", "following_plan")
