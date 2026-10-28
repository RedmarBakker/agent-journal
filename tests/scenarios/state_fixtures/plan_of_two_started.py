from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class PlanOfTwoStarted(StateFixture):
    """The user made plan 1 with two tasks and approved it in the viewer, and the agent at work started it, so its first task is in hand."""

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        plan = scenario.user_creates_plan("p", "b")
        scenario.user_adds_plan_task(plan, "first")
        scenario.user_adds_plan_task(plan, "second")
        scenario.user_approves_plan(plan)
        scenario.agent_runs(f"plan start {plan}")

    def expected(self, scenario) -> None:
        scenario.expect_plan(1, state=PlanState.STARTED)
        scenario.expect_task(1, state=TaskState.STARTED)
