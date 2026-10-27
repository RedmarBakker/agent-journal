from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class PlanJustStarted(StateFixture):
    """The user made plan 1 with one task and approved it in the viewer, and the agent at work started it, so task 1 is in hand under the plan."""

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        plan = scenario.user_creates_plan("p", "b")
        scenario.user_adds_plan_task(plan, "first")
        scenario.user_approves_plan(plan)
        scenario.agent_runs(f"plan start {plan}")

    def expected(self, scenario) -> None:
        scenario.expect_plan(1, state=PlanState.STARTED)
        scenario.expect_task(1, state=TaskState.STARTED)
        scenario.expect_stack("idle", "following_plan")
